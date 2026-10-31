import { clearToken, getToken, setToken } from "@/lib/auth";

describe("auth token storage", () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  it("stores and reads the token in session storage", () => {
    setToken("test-token");

    expect(getToken()).toBe("test-token");
    expect(sessionStorage.getItem("storage_token")).toBe("test-token");
    expect(localStorage.getItem("storage_token")).toBeNull();
  });

  it("returns null when no token exists", () => {
    expect(getToken()).toBeNull();
  });

  it("returns null when window is unavailable during server-side rendering", () => {
    const windowDescriptor = Object.getOwnPropertyDescriptor(globalThis, "window");
    sessionStorage.setItem("storage_token", "test-token");

    try {
      Object.defineProperty(globalThis, "window", {
        configurable: true,
        value: undefined,
      });
      expect(getToken()).toBeNull();
    } finally {
      if (windowDescriptor) {
        Object.defineProperty(globalThis, "window", windowDescriptor);
      }
    }
  });

  it("clears the session token", () => {
    setToken("test-token");

    clearToken();

    expect(getToken()).toBeNull();
  });
});
