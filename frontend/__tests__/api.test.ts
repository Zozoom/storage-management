import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  isLowStock,
  login,
  logout,
} from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth";

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

describe("session token storage", () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  it("stores and clears tokens in session storage, not local storage", () => {
    setToken("session-token");

    expect(getToken()).toBe("session-token");
    expect(window.sessionStorage.getItem("storage_token")).toBe("session-token");
    expect(window.localStorage.getItem("storage_token")).toBeNull();

    clearToken();
    expect(getToken()).toBeNull();
  });
});

describe("API requests", () => {
  const fetchMock = jest.spyOn(global, "fetch");
  const item = {
    id: 1,
    sku: "WDG-001",
    name: "Widget",
    description: null,
    quantity: 3,
    location: "A-01",
    min_stock: 10,
    updated_at: "2026-01-01T00:00:00",
    low_stock: true,
  };

  beforeEach(() => fetchMock.mockReset());
  afterAll(() => fetchMock.mockRestore());

  function response(json: unknown, ok = true): Response {
    return {
      ok,
      json: jest.fn().mockResolvedValue(json),
    } as unknown as Response;
  }

  it("sends login credentials to the JSON login endpoint", async () => {
    fetchMock.mockResolvedValue(response({ access_token: "token" }));

    await expect(login("admin", "admin123")).resolves.toBe("token");
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/login/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "admin123" }),
    });
  });

  it("revokes the access token on logout", async () => {
    fetchMock.mockResolvedValue(response(null));

    await expect(logout("token")).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/logout", {
      method: "POST",
      headers: {
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      },
    });
  });

  it("fetches items with a bearer token", async () => {
    fetchMock.mockResolvedValue(response([item]));

    await expect(fetchItems("token")).resolves.toEqual([item]);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", {
      headers: {
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      },
    });
  });

  it("creates an item with the expected request body and bearer token", async () => {
    const body = {
      sku: "WDG-001",
      name: "Widget",
      quantity: 3,
      location: "A-01",
      min_stock: 10,
    };
    fetchMock.mockResolvedValue(response(item));

    await expect(createItem("token", body)).resolves.toEqual(item);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", {
      method: "POST",
      headers: {
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
  });

  it("adjusts stock with the expected request body and bearer token", async () => {
    fetchMock.mockResolvedValue(response(item));

    await expect(adjustStock("token", 1, -2)).resolves.toEqual(item);
    expect(fetchMock).toHaveBeenCalledWith("/api/items/1/adjust", {
      method: "POST",
      headers: {
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ delta: -2 }),
    });
  });

  it("deletes an item with the expected URL, method, and bearer token", async () => {
    fetchMock.mockResolvedValue(response(null));

    await expect(deleteItem("token", 1)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith("/api/items/1", {
      method: "DELETE",
      headers: {
        Authorization: "Bearer token",
        "Content-Type": "application/json",
      },
    });
  });

  it("reports errors for unsuccessful responses", async () => {
    fetchMock.mockResolvedValue(response({}, false));

    await expect(login("admin", "wrong")).rejects.toThrow(
      "Invalid username or password"
    );
    fetchMock.mockResolvedValue(response({}, false));
    await expect(fetchItems("token")).rejects.toThrow("Failed to load items");
    fetchMock.mockResolvedValue(response({}, false));
    await expect(deleteItem("token", 1)).rejects.toThrow("Failed to delete item");
  });

  it("uses fallback errors when error response bodies are malformed", async () => {
    const malformedResponse = {
      ok: false,
      json: jest.fn().mockRejectedValue(new Error("invalid JSON")),
    } as unknown as Response;
    fetchMock.mockResolvedValue(malformedResponse);

    await expect(
      createItem("token", {
        sku: "WDG-001",
        name: "Widget",
        quantity: 3,
        location: "A-01",
        min_stock: 10,
      })
    ).rejects.toThrow("Failed to create item");
    fetchMock.mockResolvedValue(malformedResponse);
    await expect(adjustStock("token", 1, 1)).rejects.toThrow(
      "Failed to adjust stock"
    );
  });
});
