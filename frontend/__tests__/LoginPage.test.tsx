import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import LoginPage from "@/app/page";
import { hasSession } from "@/lib/auth";
import { login } from "@/lib/api";

jest.mock("next/navigation", () => ({ useRouter: jest.fn() }));
jest.mock("@/lib/auth", () => ({ hasSession: jest.fn() }));
jest.mock("@/lib/api", () => ({ login: jest.fn() }));

const mockPush = jest.fn();
const mockReplace = jest.fn();

beforeEach(() => {
  jest.clearAllMocks();
  (useRouter as jest.Mock).mockReturnValue({ push: mockPush, replace: mockReplace });
  (hasSession as jest.Mock).mockResolvedValue(false);
  (login as jest.Mock).mockResolvedValue(undefined);
});

describe("LoginPage", () => {
  it("navigates to the dashboard after successful cookie-based login", async () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("admin", "admin123");
      expect(mockPush).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("displays login errors and restores the submit button", async () => {
    (login as jest.Mock).mockRejectedValue(new Error("Invalid username or password"));
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Invalid username or password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeEnabled();
    expect(mockPush).not.toHaveBeenCalled();
  });

  it("redirects to the dashboard when a session already exists", async () => {
    (hasSession as jest.Mock).mockResolvedValue(true);
    render(<LoginPage />);

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/dashboard"));
  });

  it("populates the selected demo account credentials", () => {
    render(<LoginPage />);

    fireEvent.click(screen.getByRole("button", { name: "clerk" }));

    expect(screen.getByLabelText("Username")).toHaveValue("clerk");
    expect(screen.getByLabelText("Password")).toHaveValue("clerk123");
  });
});
