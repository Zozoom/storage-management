const TOKEN_KEY = "storage_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  localStorage.removeItem(TOKEN_KEY);
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
}
