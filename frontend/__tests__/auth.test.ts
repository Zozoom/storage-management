import { clearToken, getToken, setToken } from "@/lib/auth";

describe("token storage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("stores and reads the token using the storage_token key", () => {
    setToken("token-1");

    expect(localStorage.getItem("storage_token")).toBe("token-1");
    expect(getToken()).toBe("token-1");
  });

  it("removes the stored token on clear", () => {
    setToken("token-1");
    clearToken();

    expect(localStorage.getItem("storage_token")).toBeNull();
    expect(getToken()).toBeNull();
  });

  it("returns null when window is unavailable", () => {
    const descriptor = Object.getOwnPropertyDescriptor(globalThis, "window");
    Object.defineProperty(globalThis, "window", { configurable: true, value: undefined });

    try {
      expect(getToken()).toBeNull();
    } finally {
      if (descriptor) Object.defineProperty(globalThis, "window", descriptor);
    }
  });
});
