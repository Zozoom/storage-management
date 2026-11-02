import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm, type NewItem } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  it("trims text fields and converts numeric fields before submitting", async () => {
    const onSubmit = jest.fn<Promise<void>, [NewItem]>().mockResolvedValue(undefined);

    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "  Shipping box  " },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "  BOX-M  " },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "  Medium shipping box  " },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "12" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "  B-07  " },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "3" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "BOX-M",
        name: "Shipping box",
        description: "Medium shipping box",
        quantity: 12,
        location: "B-07",
        min_stock: 3,
      })
    );
  });

  it("applies defaults and omits an empty description", async () => {
    const onSubmit = jest.fn<Promise<void>, [NewItem]>().mockResolvedValue(undefined);

    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-1" },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "   " },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "" },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "WDG-1",
        name: "Widget",
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    );
  });

  it("displays callback errors and returns to the non-loading state", async () => {
    const onSubmit = jest.fn<Promise<void>, [NewItem]>().mockRejectedValue(
      new Error("Could not save item")
    );

    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("Could not save item")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
  });

  it("invokes onCancel when cancel is clicked", () => {
    const onCancel = jest.fn();

    render(<AddItemForm onSubmit={jest.fn().mockResolvedValue(undefined)} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("disables submission while the callback is pending", async () => {
    let resolveSubmit!: () => void;
    const onSubmit = jest.fn(
      () => new Promise<void>((resolve) => { resolveSubmit = resolve; })
    );

    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    const pendingButton = await screen.findByRole("button", { name: "Saving…" });
    expect(pendingButton).toBeDisabled();
    expect(onSubmit).toHaveBeenCalledTimes(1);

    await act(async () => {
      resolveSubmit();
    });
    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
  });
});
