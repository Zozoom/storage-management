import { clearToken, getToken, setToken } from "@/lib/auth";

describe("token storage helpers", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("stores, retrieves, and removes the token using the expected key", () => {
    setToken("token-123");

    expect(localStorage.getItem("storage_token")).toBe("token-123");
    expect(getToken()).toBe("token-123");

    clearToken();
    expect(localStorage.getItem("storage_token")).toBeNull();
  });

  it("returns null when window is unavailable", () => {
    const originalWindow = Object.getOwnPropertyDescriptor(globalThis, "window");
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: undefined,
    });

    try {
      expect(getToken()).toBeNull();
    } finally {
      if (originalWindow) {
        Object.defineProperty(globalThis, "window", originalWindow);
      } else {
        delete (globalThis as { window?: Window }).window;
      }
    }
  });
});
