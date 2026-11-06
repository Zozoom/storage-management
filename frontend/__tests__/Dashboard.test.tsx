import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { DashboardPage } from "@/app/dashboard/page";
import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  type Item,
} from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";

const mockReplace = jest.fn();
const mockPush = jest.fn();

jest.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace, push: mockPush }),
}));

jest.mock("@/lib/api", () => ({
  adjustStock: jest.fn(),
  createItem: jest.fn(),
  deleteItem: jest.fn(),
  fetchItems: jest.fn(),
}));

jest.mock("@/lib/auth", () => ({
  clearToken: jest.fn(),
  getToken: jest.fn(),
}));

const widget: Item = {
  id: 1,
  sku: "WDG-001",
  name: "Widget",
  description: null,
  quantity: 3,
  location: "A-01",
  min_stock: 5,
  updated_at: "2026-01-01T00:00:00",
  low_stock: true,
};

const nuts: Item = {
  id: 2,
  sku: "NUT-001",
  name: "Nuts",
  description: null,
  quantity: 12,
  location: "B-01",
  min_stock: 5,
  updated_at: "2026-01-01T00:00:00",
  low_stock: false,
};

function expectStat(label: string, value: string) {
  expect(screen.getByText(label).parentElement).toHaveTextContent(value);
}

beforeEach(() => {
  jest.clearAllMocks();
  jest.mocked(getToken).mockReturnValue("test-token");
  jest.mocked(fetchItems).mockResolvedValue([widget, nuts]);
  jest.mocked(adjustStock).mockResolvedValue({ ...widget, quantity: 4 });
  jest.mocked(createItem).mockResolvedValue({
    id: 3,
    sku: "BOX-001",
    name: "Box",
    description: null,
    quantity: 2,
    location: "C-01",
    min_stock: 1,
    updated_at: "2026-01-01T00:00:00",
    low_stock: false,
  });
  jest.mocked(deleteItem).mockResolvedValue(undefined);
  mockReplace.mockReset();
  mockPush.mockReset();
});

describe("DashboardPage", () => {
  it("redirects unauthenticated users to the login page", async () => {
    jest.mocked(getToken).mockReturnValue(null);

    render(<DashboardPage />);

    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/"));
    expect(fetchItems).not.toHaveBeenCalled();
  });

  it("clears the token and redirects when loading items fails", async () => {
    jest.mocked(fetchItems).mockRejectedValue(new Error("Failed to load items"));

    render(<DashboardPage />);

    await waitFor(() => {
      expect(clearToken).toHaveBeenCalled();
      expect(mockReplace).toHaveBeenCalledWith("/");
    });
  });

  it("filters inventory and updates stock summaries after an adjustment", async () => {
    render(<DashboardPage />);

    expect(await screen.findByText("Widget")).toBeInTheDocument();
    expect(screen.getByText("Nuts")).toBeInTheDocument();
    expectStat("Products", "2");
    expectStat("Units in stock", "15");
    expectStat("Need restocking", "1");

    fireEvent.change(screen.getByRole("searchbox", { name: "Search items" }), {
      target: { value: "widget" },
    });
    expect(screen.getByText("Widget")).toBeInTheDocument();
    expect(screen.queryByText("Nuts")).not.toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Increase Widget"));

    await waitFor(() => expectStat("Units in stock", "16"));
    expect(adjustStock).toHaveBeenCalledWith("test-token", 1, 1);
  });

  it("creates and deletes items and clears the token on logout", async () => {
    const confirm = jest.spyOn(window, "confirm").mockReturnValue(true);
    render(<DashboardPage />);

    expect(await screen.findByText("Widget")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /add item/i }));
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Box" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "BOX-001" },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "C-01" },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("Box")).toBeInTheDocument();
    expect(createItem).toHaveBeenCalledWith(
      "test-token",
      expect.objectContaining({
        sku: "BOX-001",
        name: "Box",
        quantity: 2,
        location: "C-01",
        min_stock: 1,
      })
    );
    expectStat("Products", "3");
    expectStat("Units in stock", "17");

    fireEvent.click(screen.getByLabelText("Delete Widget"));
    await waitFor(() => expect(screen.queryByText("Widget")).not.toBeInTheDocument());
    expect(confirm).toHaveBeenCalledWith("Delete this item?");
    expect(deleteItem).toHaveBeenCalledWith("test-token", 1);
    expectStat("Products", "2");
    expectStat("Units in stock", "14");

    fireEvent.click(screen.getByRole("button", { name: "Log out" }));
    expect(clearToken).toHaveBeenCalled();
    expect(mockPush).toHaveBeenCalledWith("/");

    confirm.mockRestore();
  });
});
