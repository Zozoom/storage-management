import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  it("trims submitted values, converts numbers, uses defaults, and omits a blank description", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "  Shipping box  " },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "  BOX-M  " },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "   " },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "BOX-M",
        name: "Shipping box",
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    );
  });

  it("shows submission errors, resets loading, and invokes cancel", async () => {
    const onSubmit = jest
      .fn()
      .mockRejectedValueOnce(new Error("Failed to add item"));
    const onCancel = jest.fn();
    render(<AddItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Shipping box" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "BOX-M" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("Failed to add item")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
