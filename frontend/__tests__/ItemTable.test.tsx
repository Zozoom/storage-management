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

const zeroStockItem: Item = {
  ...sample[0],
  id: 2,
  sku: "BOX-001",
  name: "Box",
  quantity: 0,
};

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

  it("calls onAdjust when decreasing an item with positive quantity", () => {
    const onAdjust = jest.fn();
    render(
      <ItemTable
        items={sample}
        onAdjust={onAdjust}
        onDelete={jest.fn()}
        busyId={null}
      />
    );

    fireEvent.click(screen.getByLabelText("Decrease Widget"));

    expect(onAdjust).toHaveBeenCalledWith(1, -1);
  });

  it("disables decreasing an item when its quantity is zero", () => {
    const onAdjust = jest.fn();
    render(
      <ItemTable
        items={[zeroStockItem]}
        onAdjust={onAdjust}
        onDelete={jest.fn()}
        busyId={null}
      />
    );

    expect(screen.getByLabelText("Decrease Box")).toBeDisabled();
    fireEvent.click(screen.getByLabelText("Decrease Box"));
    expect(onAdjust).not.toHaveBeenCalled();
  });

  it("calls onDelete for the selected item", () => {
    const onDelete = jest.fn();
    render(
      <ItemTable
        items={sample}
        onAdjust={jest.fn()}
        onDelete={onDelete}
        busyId={null}
      />
    );

    fireEvent.click(screen.getByLabelText("Delete Widget"));

    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("disables actions only for the busy item", () => {
    render(
      <ItemTable
        items={[sample[0], zeroStockItem]}
        onAdjust={jest.fn()}
        onDelete={jest.fn()}
        busyId={1}
      />
    );

    expect(screen.getByLabelText("Decrease Widget")).toBeDisabled();
    expect(screen.getByLabelText("Increase Widget")).toBeDisabled();
    expect(screen.getByLabelText("Delete Widget")).toBeDisabled();

    expect(screen.getByLabelText("Increase Box")).toBeEnabled();
    expect(screen.getByLabelText("Delete Box")).toBeEnabled();
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
