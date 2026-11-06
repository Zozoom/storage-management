const TOKEN_KEY = "storage_token";
const STORAGE_ERROR =
  "Authentication storage is unavailable. Enable browser storage and try again.";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    throw new Error(STORAGE_ERROR);
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    throw new Error(STORAGE_ERROR);
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    throw new Error(STORAGE_ERROR);
  }
}
