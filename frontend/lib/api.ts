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

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function login(
  username: string,
  password: string
): Promise<string> {
  const res = await fetch(`${API_URL}/api/auth/login/json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new Error("Invalid username or password");
  }
  const data = await res.json();
  return data.access_token as string;
}

export async function logout(token: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to log out");
}

export async function fetchItems(token: string): Promise<Item[]> {
  const res = await fetch(`${API_URL}/api/items`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load items");
  return res.json();
}

export async function createItem(
  token: string,
  body: {
    sku: string;
    name: string;
    description?: string;
    quantity: number;
    location: string;
    min_stock: number;
  }
): Promise<Item> {
  const res = await fetch(`${API_URL}/api/items`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create item");
  }
  return res.json();
}

export async function adjustStock(
  token: string,
  id: number,
  delta: number
): Promise<Item> {
  const res = await fetch(`${API_URL}/api/items/${id}/adjust`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ delta }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to adjust stock");
  }
  return res.json();
}

export async function deleteItem(token: string, id: number): Promise<void> {
  const res = await fetch(`${API_URL}/api/items/${id}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to delete item");
}

export function isLowStock(item: Pick<Item, "quantity" | "min_stock">): boolean {
  return item.quantity < item.min_stock;
}
