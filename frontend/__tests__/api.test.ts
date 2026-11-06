import { isLowStock, login, fetchItems, createItem, adjustStock, deleteItem } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

function mockResponse(body: unknown, ok = true): Response {
  return {
    ok,
    json: jest.fn().mockResolvedValue(body),
  } as unknown as Response;
}

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

describe("API client requests", () => {
  const fetchMock = jest.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    global.fetch = fetchMock;
  });

  it("sends login credentials to the JSON login endpoint", async () => {
    fetchMock.mockResolvedValue(mockResponse({ access_token: "token-123" }));

    await expect(login("admin", "admin123")).resolves.toBe("token-123");
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/auth/login/json`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "admin123" }),
    });
  });

  it("sends an authenticated item list request", async () => {
    fetchMock.mockResolvedValue(mockResponse([]));

    await expect(fetchItems("token-123")).resolves.toEqual([]);
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/items`, {
      headers: {
        Authorization: "Bearer token-123",
        "Content-Type": "application/json",
      },
    });
  });

  it("sends an authenticated item creation request with its body", async () => {
    const item = {
      sku: "NEW-1",
      name: "New item",
      description: "Test item",
      quantity: 4,
      location: "A-02",
      min_stock: 2,
    };
    fetchMock.mockResolvedValue(mockResponse({ id: 1, ...item }));

    await expect(createItem("token-123", item)).resolves.toEqual({ id: 1, ...item });
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/items`, {
      method: "POST",
      headers: {
        Authorization: "Bearer token-123",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(item),
    });
  });

  it("sends an authenticated stock adjustment request with its delta", async () => {
    fetchMock.mockResolvedValue(mockResponse({ id: 7, quantity: 9 }));

    await expect(adjustStock("token-123", 7, -1)).resolves.toEqual({ id: 7, quantity: 9 });
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/items/7/adjust`, {
      method: "POST",
      headers: {
        Authorization: "Bearer token-123",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ delta: -1 }),
    });
  });

  it("sends an authenticated item deletion request", async () => {
    fetchMock.mockResolvedValue(mockResponse(null));

    await expect(deleteItem("token-123", 7)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/items/7`, {
      method: "DELETE",
      headers: {
        Authorization: "Bearer token-123",
        "Content-Type": "application/json",
      },
    });
  });
});

describe("API client errors", () => {
  const fetchMock = jest.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    global.fetch = fetchMock;
  });

  it("rejects login failures with the expected error", async () => {
    fetchMock.mockResolvedValue(mockResponse({}, false));

    await expect(login("admin", "wrong")).rejects.toThrow("Invalid username or password");
  });

  it("rejects item list failures with the expected error", async () => {
    fetchMock.mockResolvedValue(mockResponse({}, false));

    await expect(fetchItems("token-123")).rejects.toThrow("Failed to load items");
  });

  it("uses the server detail for item creation failures", async () => {
    fetchMock.mockResolvedValue(mockResponse({ detail: "SKU already exists" }, false));

    await expect(
      createItem("token-123", {
        sku: "NEW-1",
        name: "New item",
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    ).rejects.toThrow("SKU already exists");
  });

  it("uses the default error when item creation failure has no detail", async () => {
    fetchMock.mockResolvedValue(mockResponse({}, false));

    await expect(
      createItem("token-123", {
        sku: "NEW-1",
        name: "New item",
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    ).rejects.toThrow("Failed to create item");
  });

  it("uses the server detail for stock adjustment failures", async () => {
    fetchMock.mockResolvedValue(mockResponse({ detail: "Insufficient stock" }, false));

    await expect(adjustStock("token-123", 7, -20)).rejects.toThrow("Insufficient stock");
  });

  it("uses the default error when stock adjustment failure has no detail", async () => {
    fetchMock.mockResolvedValue(mockResponse({}, false));

    await expect(adjustStock("token-123", 7, -20)).rejects.toThrow("Failed to adjust stock");
  });

  it("rejects item deletion failures with the expected error", async () => {
    fetchMock.mockResolvedValue(mockResponse({}, false));

    await expect(deleteItem("token-123", 7)).rejects.toThrow("Failed to delete item");
  });
});
