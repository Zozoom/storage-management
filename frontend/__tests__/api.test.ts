import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  getCurrentUser,
  isLowStock,
  login,
} from "@/lib/api";

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

describe("cookie-based authentication", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("submits login with credentials included without exposing a token response", async () => {
    const fetchMock = jest.spyOn(global, "fetch").mockResolvedValue({ ok: true } as Response);

    await expect(login("admin", "admin123")).resolves.toBeUndefined();

    expect(fetchMock).toHaveBeenCalledWith("/api/auth/login/json", {
      credentials: "include",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "admin123" }),
    });
  });

  it("rejects unsuccessful login responses", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({ ok: false } as Response);

    await expect(login("admin", "wrong-password")).rejects.toThrow(
      "Invalid username or password"
    );
  });

  it("checks the session through the current-user endpoint with credentials", async () => {
    const fetchMock = jest.spyOn(global, "fetch").mockResolvedValue({ ok: true } as Response);

    await expect(getCurrentUser()).resolves.toBe(true);
    expect(fetchMock).toHaveBeenCalledWith("/api/auth/me", { credentials: "include" });
  });
});

describe("inventory API requests", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("fetches items using the session cookie", async () => {
    const items = [{ id: 1, sku: "SKU-1", name: "Item" }];
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(items) } as unknown as Response);

    await expect(fetchItems()).resolves.toEqual(items);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", { credentials: "include" });
  });

  it("creates an item with the expected URL, method, credentials, and request body", async () => {
    const body = {
      sku: "NEW-1",
      name: "New Item",
      description: "A description",
      quantity: 4,
      location: "A-02",
      min_stock: 2,
    };
    const created = { id: 2, ...body };
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(created) } as unknown as Response);

    await expect(createItem(body)).resolves.toEqual(created);
    expect(fetchMock).toHaveBeenCalledWith("/api/items", {
      credentials: "include",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  });

  it("surfaces create errors from the server response", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      json: jest.fn().mockResolvedValue({ detail: "SKU already exists" }),
    } as unknown as Response);

    await expect(
      createItem({ sku: "DUP", name: "Duplicate", quantity: 0, location: "A-01", min_stock: 5 })
    ).rejects.toThrow("SKU already exists");
  });

  it("uses the default create error when the response body is invalid", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new Error("Invalid JSON")),
    } as unknown as Response);

    await expect(
      createItem({ sku: "NEW", name: "New Item", quantity: 0, location: "A-01", min_stock: 5 })
    ).rejects.toThrow("Failed to create item");
  });

  it("adjusts stock with the expected URL, method, credentials, and request body", async () => {
    const updated = { id: 7, quantity: 12 };
    const fetchMock = jest
      .spyOn(global, "fetch")
      .mockResolvedValue({ ok: true, json: jest.fn().mockResolvedValue(updated) } as unknown as Response);

    await expect(adjustStock(7, 2)).resolves.toEqual(updated);
    expect(fetchMock).toHaveBeenCalledWith("/api/items/7/adjust", {
      credentials: "include",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ delta: 2 }),
    });
  });

  it("surfaces adjust errors from the server response", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      json: jest.fn().mockResolvedValue({ detail: "Insufficient stock" }),
    } as unknown as Response);

    await expect(adjustStock(7, -20)).rejects.toThrow("Insufficient stock");
  });

  it("uses the default adjust error when the response body is invalid", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: false,
      json: jest.fn().mockRejectedValue(new Error("Invalid JSON")),
    } as unknown as Response);

    await expect(adjustStock(7, -1)).rejects.toThrow("Failed to adjust stock");
  });

  it("deletes an item using the expected URL, method, and session credentials", async () => {
    const fetchMock = jest.spyOn(global, "fetch").mockResolvedValue({ ok: true } as Response);

    await expect(deleteItem(7)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith("/api/items/7", {
      credentials: "include",
      method: "DELETE",
    });
  });

  it("rejects unsuccessful delete responses", async () => {
    jest.spyOn(global, "fetch").mockResolvedValue({ ok: false } as Response);

    await expect(deleteItem(7)).rejects.toThrow("Failed to delete item");
  });
});
