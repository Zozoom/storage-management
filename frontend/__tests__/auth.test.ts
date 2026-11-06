import { clearToken, getToken, setToken } from "@/lib/auth";

const storageError =
  "Authentication storage is unavailable. Enable browser storage and try again.";

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe("token persistence", () => {
  it("sets and retrieves the token using the storage_token key", () => {
    setToken("session-token");

    expect(localStorage.getItem("storage_token")).toBe("session-token");
    expect(getToken()).toBe("session-token");
  });

  it("clears the token using the storage_token key", () => {
    setToken("session-token");

    clearToken();

    expect(localStorage.getItem("storage_token")).toBeNull();
    expect(getToken()).toBeNull();
  });

  it("returns null when window is unavailable", () => {
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

describe("authentication storage failures", () => {
  it("reports an error when reading storage is blocked", () => {
    jest.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("Storage is disabled");
    });

    expect(() => getToken()).toThrow(storageError);
  });

  it("reports an error when writing storage is blocked", () => {
    jest.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("Storage is disabled");
    });

    expect(() => setToken("session-token")).toThrow(storageError);
  });

  it("reports an error when removing a token is blocked", () => {
    jest.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
      throw new Error("Storage is disabled");
    });

    expect(() => clearToken()).toThrow(storageError);
  });
});
