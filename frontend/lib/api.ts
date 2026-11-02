// Empty = same origin: on Vercel /api/* is routed to the backend service.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export type Item = {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  quantity: number;
  location: string;
  min_stock: number;
  updated_at: string;
  low_stock: boolean;
};

const SESSION_OPTIONS: RequestInit = { credentials: "include" };

function jsonHeaders(): HeadersInit {
  return { "Content-Type": "application/json" };
}

export async function login(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/auth/login/json`, {
    ...SESSION_OPTIONS,
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error("Invalid username or password");
  }
}

export async function getCurrentUser(): Promise<boolean> {
  const res = await fetch(`${API_URL}/api/auth/me`, SESSION_OPTIONS);
  return res.ok;
}

export async function logoutSession(): Promise<void> {
  const res = await fetch(`${API_URL}/api/auth/logout`, {
    ...SESSION_OPTIONS,
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to log out");
}

export async function fetchItems(): Promise<Item[]> {
  const res = await fetch(`${API_URL}/api/items`, SESSION_OPTIONS);
  if (!res.ok) throw new Error("Failed to load items");
  return res.json();
}

export async function createItem(body: {
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  location: string;
  min_stock: number;
}): Promise<Item> {
  const res = await fetch(`${API_URL}/api/items`, {
    ...SESSION_OPTIONS,
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create item");
  }
  return res.json();
}

export async function adjustStock(id: number, delta: number): Promise<Item> {
  const res = await fetch(`${API_URL}/api/items/${id}/adjust`, {
    ...SESSION_OPTIONS,
    method: "POST",
    headers: jsonHeaders(),
    body: JSON.stringify({ delta }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to adjust stock");
  }
  return res.json();
}

export async function deleteItem(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    ...SESSION_OPTIONS,
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete item");
}

export function isLowStock(item: Pick<Item, "quantity" | "min_stock">): boolean {
  return item.quantity < item.min_stock;
}
