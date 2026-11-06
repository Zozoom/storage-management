import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { getToken, setToken } from "@/lib/auth";
import LoginPage from "@/app/page";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/api", () => ({ login: jest.fn() }));
jest.mock("@/lib/auth", () => ({
  getToken: jest.fn(),
  setToken: jest.fn(),
}));

describe("LoginPage", () => {
  const push = jest.fn();
  const replace = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    jest.mocked(useRouter).mockReturnValue({ push, replace } as ReturnType<typeof useRouter>);
    jest.mocked(getToken).mockReturnValue(null);
  });

  it("stores the token and navigates to the dashboard after a successful login", async () => {
    jest.mocked(login).mockResolvedValue("access-token");
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(setToken).toHaveBeenCalledWith("access-token");
      expect(push).toHaveBeenCalledWith("/dashboard");
    });
    expect(login).toHaveBeenCalledWith("admin", "admin123");
  });

  it("shows a login error, restores the submit button, and does not store a token on failure", async () => {
    jest.mocked(login).mockRejectedValue(new Error("Invalid username or password"));
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid username or password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeEnabled();
    expect(setToken).not.toHaveBeenCalled();
    expect(push).not.toHaveBeenCalled();
  });

  it("redirects to the dashboard when a token already exists", async () => {
    jest.mocked(getToken).mockReturnValue("existing-token");
    render(<LoginPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
  });
});
