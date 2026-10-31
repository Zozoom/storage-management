import { render, screen, fireEvent } from "@testing-library/react";
import { ItemTable } from "@/components/ItemTable";
import type { Item } from "@/lib/api";

const sample: Item[] = [
  {
    id: 1,
    sku: "WDG-001",
    name: "Widget",
    description: "A test widget",
    quantity: 3,
    location: "A-01",
    min_stock: 10,
    updated_at: "2026-01-01T00:00:00",
    low_stock: true,
  },
];

describe("ItemTable", () => {
  it("renders item rows and low stock badge", () => {
    render(
      <ItemTable
        items={sample}
        onAdjust={jest.fn()}
        onDelete={jest.fn()}
        busyId={null}
      />
    );
    expect(screen.getByText("WDG-001")).toBeInTheDocument();
    expect(screen.getByText("Widget")).toBeInTheDocument();
    expect(screen.getByText("Low stock")).toBeInTheDocument();
  });

  it("calls onAdjust when +1 is clicked", () => {
    const onAdjust = jest.fn();
    render(
      <ItemTable
        items={sample}
        onAdjust={onAdjust}
        onDelete={jest.fn()}
        busyId={null}
      />
    );
    fireEvent.click(screen.getByLabelText("Increase Widget"));
    expect(onAdjust).toHaveBeenCalledWith(1, 1);
  });

  it("shows empty state", () => {
    render(
      <ItemTable
        items={[]}
        onAdjust={jest.fn()}
        onDelete={jest.fn()}
        busyId={null}
      />
    );
    expect(screen.getByText(/No items found/)).toBeInTheDocument();
  });
});
