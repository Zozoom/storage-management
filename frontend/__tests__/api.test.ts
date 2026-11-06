import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  isLowStock,
  login,
  logout,
  type Item,
} from "@/lib/api";

afterEach(() => {
  jest.restoreAllMocks();
});

function mockResponse(ok: boolean, json: () => Promise<unknown>): Response {
  return { ok, json } as Response;
}

const item: Item = {
  id: 1,
  sku: "WDG-001",
  name: "Widget",
  description: "A test widget",
  quantity: 3,
  location: "A-01",
  min_stock: 10,
  updated_at: "2026-01-01T00:00:00",
  low_stock: true,
};

describe("isLowStock", () => {
  it("returns true when quantity is below min_stock", () => {
    expect(isLowStock({ quantity: 4, min_stock: 5 })).toBe(true);
  });

  it("returns false when quantity equals min_stock", () => {
    expect(isLowStock({ quantity: 5, min_stock: 5 })).toBe(false);
  });

  it("returns false when quantity is above min_stock", () => {
    expect(isLowStock({ quantity: 20, min_stock: 5 })).toBe(false);
  });
});

describe("login", () => {
  it("sends credentials as JSON and returns the access token", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(
        mockResponse(true, async () => ({ access_token: "session-token" }))
      );

    await expect(login("admin", "admin123")).resolves.toBe("session-token");
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/login/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "admin123" }),
    });
  });

  it("rejects unsuccessful responses with the login error", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue(mockResponse(false, async () => ({})));

    await expect(login("admin", "wrong")).rejects.toThrow(
      "Invalid username or password"
    );
  });
});

describe("fetchItems", () => {
  it("sends the bearer token and returns the item list", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(true, async () => [item]));

    await expect(fetchItems("session-token")).resolves.toEqual([item]);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", {
      headers: {
        Authorization: "Bearer session-token",
        "Content-Type": "application/json",
      },
    });
  });

  it("rejects unsuccessful responses with the loading error", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue(mockResponse(false, async () => []));

    await expect(fetchItems("session-token")).rejects.toThrow("Failed to load items");
  });
});

describe("createItem", () => {
  const body = {
    sku: "WDG-001",
    name: "Widget",
    description: "A test widget",
    quantity: 3,
    location: "A-01",
    min_stock: 10,
  };

  it("sends the item as JSON and returns the created item", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(true, async () => item));

    await expect(createItem("session-token", body)).resolves.toEqual(item);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", {
      method: "POST",
      headers: {
        Authorization: "Bearer session-token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
  });

  it("uses the backend detail for unsuccessful responses", async () => {
    jest
      .spyOn(global, "fetch")
      .mockResolvedValue(
        mockResponse(false, async () => ({ detail: "SKU already exists" }))
      );

    await expect(createItem("session-token", body)).rejects.toThrow(
      "SKU already exists"
    );
  });

  it("uses the fallback error when the error body is malformed", async () => {
    jest
      .spyOn(global, "fetch")
      .mockResolvedValue(
        mockResponse(false, async () => {
          throw new Error("Invalid JSON");
        })
      );

    await expect(createItem("session-token", body)).rejects.toThrow(
      "Failed to create item"
    );
  });
});

describe("adjustStock", () => {
  it("sends the stock delta as JSON and returns the updated item", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(true, async () => item));

    await expect(adjustStock("session-token", 1, -2)).resolves.toEqual(item);
    expect(fetchMock).toHaveBeenCalledWith("/api/items/1/adjust", {
      method: "POST",
      headers: {
        Authorization: "Bearer session-token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ delta: -2 }),
    });
  });

  it("uses the backend detail for unsuccessful responses", async () => {
    jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(false, async () => ({ detail: "Insufficient stock" })));

    await expect(adjustStock("session-token", 1, -20)).rejects.toThrow(
      "Insufficient stock"
    );
  });

  it("uses the fallback error when the error body is malformed", async () => {
    jest
      .spyOn(global, "fetch")
      .mockResolvedValue(
        mockResponse(false, async () => {
          throw new Error("Invalid JSON");
        })
      );

    await expect(adjustStock("session-token", 1, 1)).rejects.toThrow(
      "Failed to adjust stock"
    );
  });
});

describe("deleteItem", () => {
  it("sends an authenticated delete request and resolves on success", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(true, async () => undefined));

    await expect(deleteItem("session-token", 1)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith("/api/items/1", {
      method: "DELETE",
      headers: {
        Authorization: "Bearer session-token",
        "Content-Type": "application/json",
      },
    });
  });

  it("rejects unsuccessful responses with the delete error", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue(mockResponse(false, async () => ({})));

    await expect(deleteItem("session-token", 1)).rejects.toThrow(
      "Failed to delete item"
    );
  });
});

describe("logout", () => {
  it("requests server-side revocation with the bearer token", async () => {
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue(mockResponse(true, async () => undefined));

    await expect(logout("session-token")).resolves.toBeUndefined();

    expect(fetchMock).toHaveBeenCalledWith("/api/auth/logout", {
      method: "POST",
      headers: {
        Authorization: "Bearer session-token",
        "Content-Type": "application/json",
      },
    });
  });

  it("rejects unsuccessful responses with the logout error", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue(mockResponse(false, async () => ({})));

    await expect(logout("session-token")).rejects.toThrow("Failed to log out");
  });
});
