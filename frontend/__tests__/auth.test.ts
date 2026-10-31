import { clearToken, getToken, setToken } from "@/lib/auth";

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});

describe("token storage", () => {
  it("stores and reads the token in session storage, not local storage", () => {
    setToken("session-token");

    expect(getToken()).toBe("session-token");
    expect(sessionStorage.getItem("storage_token")).toBe("session-token");
    expect(localStorage.getItem("storage_token")).toBeNull();
  });

  it("returns null when no token is stored", () => {
    expect(getToken()).toBeNull();
  });

  it("returns null when window is unavailable", () => {
    const windowDescriptor = Object.getOwnPropertyDescriptor(globalThis, "window");

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

  it("removes any legacy local-storage token when reading", () => {
    localStorage.setItem("storage_token", "legacy-token");

    expect(getToken()).toBeNull();
    expect(localStorage.getItem("storage_token")).toBeNull();
  });

  it("clears the token from both storage locations", () => {
    localStorage.setItem("storage_token", "legacy-token");
    sessionStorage.setItem("storage_token", "session-token");

    clearToken();

    expect(localStorage.getItem("storage_token")).toBeNull();
    expect(sessionStorage.getItem("storage_token")).toBeNull();
  });
});
