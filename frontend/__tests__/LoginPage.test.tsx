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
    (useRouter as jest.Mock).mockReturnValue({ push, replace });
    (getToken as jest.Mock).mockReturnValue(null);
  });

  it("stores the returned token and navigates to the dashboard on successful login", async () => {
    (login as jest.Mock).mockResolvedValue("token-123");
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(setToken).toHaveBeenCalledWith("token-123");
      expect(push).toHaveBeenCalledWith("/dashboard");
    });
    expect(login).toHaveBeenCalledWith("admin", "admin123");
  });

  it("displays login errors and resets the loading state", async () => {
    (login as jest.Mock).mockRejectedValue(new Error("Invalid username or password"));
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid username or password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeEnabled();
    expect(setToken).not.toHaveBeenCalled();
    expect(push).not.toHaveBeenCalled();
  });

  it("redirects to the dashboard when a token already exists", async () => {
    (getToken as jest.Mock).mockReturnValue("existing-token");
    render(<LoginPage />);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/dashboard"));
    expect(login).not.toHaveBeenCalled();
  });
});
