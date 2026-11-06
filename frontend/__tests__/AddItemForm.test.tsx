import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  it("trims submitted text and converts numeric fields", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "  Shipping box  " },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "  BOX-M  " },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "  Small box  " },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "12" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "  B-02  " },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "4" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "BOX-M",
        name: "Shipping box",
        description: "Small box",
        quantity: 12,
        location: "B-02",
        min_stock: 4,
      })
    );
  });

  it("uses defaults for blank numeric and location fields and omits a blank description", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Item" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "ITEM-1" },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "   " },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "   " },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "ITEM-1",
        name: "Item",
        description: undefined,
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    );
  });

  it("displays callback errors and restores the submit button", async () => {
    const onSubmit = jest.fn().mockRejectedValue(new Error("Save failed"));
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Item" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "ITEM-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("Save failed")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
  });

  it("invokes cancel and disables submission while the callback is pending", async () => {
    let resolveSubmit!: () => void;
    const onSubmit = jest.fn(
      () =>
        new Promise<void>((resolve) => {
          resolveSubmit = resolve;
        })
    );
    const onCancel = jest.fn();
    render(<AddItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalledTimes(1);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Item" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "ITEM-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
    resolveSubmit();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled()
    );
  });
});
