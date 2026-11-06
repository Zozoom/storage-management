import { clearToken, getToken, setToken } from "@/lib/auth";

describe("token storage helpers", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("stores and retrieves a token using the expected key", () => {
    setToken("test-token");

    expect(sessionStorage.getItem("storage_token")).toBe("test-token");
    expect(getToken()).toBe("test-token");
  });

  it("clears the stored token", () => {
    setToken("test-token");

    clearToken();

    expect(sessionStorage.getItem("storage_token")).toBeNull();
    expect(getToken()).toBeNull();
  });

  it("returns null when no browser window is available", () => {
    const windowDescriptor = Object.getOwnPropertyDescriptor(globalThis, "window");
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: undefined,
    });

    try {
      expect(getToken()).toBeNull();
    } finally {
      if (windowDescriptor) {
        Object.defineProperty(globalThis, "window", windowDescriptor);
      } else {
        Reflect.deleteProperty(globalThis, "window");
      }
    }
  });
});
