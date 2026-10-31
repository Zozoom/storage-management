import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  isLowStock,
  login,
  type Item,
} from "@/lib/api";

function makeResponse(data: unknown, ok = true): Response {
  return {
    ok,
    json: jest.fn().mockResolvedValue(data),
  } as unknown as Response;
}

function mockFetch() {
  return jest.spyOn(global, "fetch");
}

afterEach(() => {
  jest.restoreAllMocks();
});

describe("API client", () => {
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

  it("logs in and returns the access token", async () => {
    const fetchSpy = mockFetch().mockResolvedValue(
      makeResponse({ access_token: "test-token" })
    );

    await expect(login("admin", "admin123")).resolves.toBe("test-token");
    expect(fetchSpy).toHaveBeenCalledWith("/api/auth/login/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "admin123" }),
    });
  });

  it("rejects failed login with the intended error", async () => {
    mockFetch().mockResolvedValue(makeResponse({}, false));

    await expect(login("admin", "wrong")).rejects.toThrow(
      "Invalid username or password"
    );
  });

  it("fetches items with a bearer token and returns the item data", async () => {
    const fetchSpy = mockFetch().mockResolvedValue(makeResponse([item]));

    await expect(fetchItems("test-token")).resolves.toEqual([item]);
    expect(fetchSpy).toHaveBeenCalledWith("/api/items", {
      headers: {
        Authorization: "Bearer test-token",
        "Content-Type": "application/json",
      },
    });
  });

  it("rejects failed item listing with the intended error", async () => {
    mockFetch().mockResolvedValue(makeResponse({}, false));

    await expect(fetchItems("test-token")).rejects.toThrow("Failed to load items");
  });

  it("creates an item with the expected request and returns the created item", async () => {
    const body = {
      sku: "WDG-001",
      name: "Widget",
      description: "A test widget",
      quantity: 3,
      location: "A-01",
      min_stock: 10,
    };
    const fetchSpy = mockFetch().mockResolvedValue(makeResponse(item));

    await expect(createItem("test-token", body)).resolves.toEqual(item);
    expect(fetchSpy).toHaveBeenCalledWith("/api/items", {
      method: "POST",
      headers: {
        Authorization: "Bearer test-token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
  });

  it("uses JSON error details when item creation fails", async () => {
    mockFetch().mockResolvedValue(makeResponse({ detail: "SKU already exists" }, false));

    await expect(
      createItem("test-token", {
        sku: "WDG-001",
        name: "Widget",
        quantity: 3,
        location: "A-01",
        min_stock: 10,
      })
    ).rejects.toThrow("SKU already exists");
  });

  it("uses the fallback error when item creation returns invalid JSON", async () => {
    mockFetch().mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new Error("Invalid JSON")),
    } as unknown as Response);

    await expect(
      createItem("test-token", {
        sku: "WDG-001",
        name: "Widget",
        quantity: 3,
        location: "A-01",
        min_stock: 10,
      })
    ).rejects.toThrow("Failed to create item");
  });

  it("adjusts stock with the expected request and returns the updated item", async () => {
    const fetchSpy = mockFetch().mockResolvedValue(makeResponse(item));

    await expect(adjustStock("test-token", 1, -2)).resolves.toEqual(item);
    expect(fetchSpy).toHaveBeenCalledWith("/api/items/1/adjust", {
      method: "POST",
      headers: {
        Authorization: "Bearer test-token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ delta: -2 }),
    });
  });

  it("uses JSON error details when stock adjustment fails", async () => {
    mockFetch().mockResolvedValue(makeResponse({ detail: "Insufficient stock" }, false));

    await expect(adjustStock("test-token", 1, -5)).rejects.toThrow(
      "Insufficient stock"
    );
  });

  it("uses the fallback error when stock adjustment returns invalid JSON", async () => {
    mockFetch().mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new Error("Invalid JSON")),
    } as unknown as Response);

    await expect(adjustStock("test-token", 1, -5)).rejects.toThrow(
      "Failed to adjust stock"
    );
  });

  it("deletes an item with the expected request", async () => {
    const fetchSpy = mockFetch().mockResolvedValue(makeResponse(null));

    await expect(deleteItem("test-token", 1)).resolves.toBeUndefined();
    expect(fetchSpy).toHaveBeenCalledWith("/api/items/1", {
      method: "DELETE",
      headers: {
        Authorization: "Bearer test-token",
        "Content-Type": "application/json",
      },
    });
  });

  it("rejects failed item deletion with the intended error", async () => {
    mockFetch().mockResolvedValue(makeResponse({}, false));

    await expect(deleteItem("test-token", 1)).rejects.toThrow("Failed to delete item");
  });
});

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
