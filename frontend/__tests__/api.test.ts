import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  isLowStock,
  login,
} from "@/lib/api";

const response = (ok: boolean, body?: unknown) =>
  ({ ok, json: jest.fn().mockResolvedValue(body) }) as unknown as Response;

beforeEach(() => {
  global.fetch = jest.fn();
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

describe("API requests", () => {
  it("sends JSON credentials and returns the login token", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(true, { access_token: "token-1" }));

    await expect(login("alice", "secret")).resolves.toBe("token-1");
    expect(fetch).toHaveBeenCalledWith("/api/auth/login/json", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "alice", password: "secret" }),
    });
  });

  it("reports a failed login response", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(false));

    await expect(login("alice", "wrong")).rejects.toThrow("Invalid username or password");
  });

  it("includes the bearer token when listing items", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(true, []));

    await expect(fetchItems("token-1")).resolves.toEqual([]);
    expect(fetch).toHaveBeenCalledWith("/api/items", {
      headers: { Authorization: "Bearer token-1", "Content-Type": "application/json" },
    });
  });

  it("reports a failed list response", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(false));
    await expect(fetchItems("token-1")).rejects.toThrow("Failed to load items");
  });

  it("sends the item payload when creating an item", async () => {
    const item = { id: 1, sku: "A-1" };
    const body = { sku: "A-1", name: "Part", quantity: 2, location: "A-01", min_stock: 1 };
    (fetch as jest.Mock).mockResolvedValue(response(true, item));

    await expect(createItem("token-1", body)).resolves.toEqual(item);
    expect(fetch).toHaveBeenCalledWith("/api/items", {
      method: "POST",
      headers: { Authorization: "Bearer token-1", "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  });

  it("handles failed create responses with malformed or missing JSON", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(false));
    await expect(createItem("token-1", { sku: "A", name: "Part", quantity: 1, location: "A", min_stock: 0 }))
      .rejects.toThrow("Failed to create item");

    (fetch as jest.Mock).mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new SyntaxError("invalid JSON")),
    });
    await expect(createItem("token-1", { sku: "A", name: "Part", quantity: 1, location: "A", min_stock: 0 }))
      .rejects.toThrow("Failed to create item");
  });

  it("sends the stock adjustment payload", async () => {
    const item = { id: 4, quantity: 7 };
    (fetch as jest.Mock).mockResolvedValue(response(true, item));

    await expect(adjustStock("token-1", 4, 2)).resolves.toEqual(item);
    expect(fetch).toHaveBeenCalledWith("/api/items/4/adjust", {
      method: "POST",
      headers: { Authorization: "Bearer token-1", "Content-Type": "application/json" },
      body: JSON.stringify({ delta: 2 }),
    });
  });

  it("handles failed adjustment responses with malformed or missing JSON", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(false));
    await expect(adjustStock("token-1", 4, -1)).rejects.toThrow("Failed to adjust stock");

    (fetch as jest.Mock).mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new SyntaxError("invalid JSON")),
    });
    await expect(adjustStock("token-1", 4, -1)).rejects.toThrow("Failed to adjust stock");
  });

  it("sends authenticated delete requests and reports failures", async () => {
    (fetch as jest.Mock).mockResolvedValue(response(true));
    await expect(deleteItem("token-1", 4)).resolves.toBeUndefined();
    expect(fetch).toHaveBeenCalledWith("/api/items/4", {
      method: "DELETE",
      headers: { Authorization: "Bearer token-1", "Content-Type": "application/json" },
    });

    (fetch as jest.Mock).mockResolvedValue(response(false));
    await expect(deleteItem("token-1", 4)).rejects.toThrow("Failed to delete item");
  });
});
