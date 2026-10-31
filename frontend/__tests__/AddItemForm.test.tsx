import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  it("submits trimmed values and omits a blank optional description", () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "  Widget  " },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "  WDG-001  " },
    });
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "   " },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "12" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "  A-02  " },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: " 3 " },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(onSubmit).toHaveBeenCalledWith({
      name: "Widget",
      sku: "WDG-001",
      description: undefined,
      quantity: 12,
      location: "A-02",
      min_stock: 3,
    });
  });

  it("uses default values when quantity, location, and minimum stock are blank", () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-001" },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "" },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(onSubmit).toHaveBeenCalledWith({
      name: "Widget",
      sku: "WDG-001",
      description: undefined,
      quantity: 0,
      location: "A-01",
      min_stock: 5,
    });
  });

  it("shows a rejected callback's error and restores the submit button", async () => {
    const onSubmit = jest.fn().mockRejectedValue(new Error("SKU already exists"));
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("SKU already exists")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
  });

  it("calls cancel and disables submission while the callback is pending", async () => {
    let finishSubmission!: () => void;
    const onSubmit = jest.fn(
      () => new Promise<void>((resolve) => {
        finishSubmission = resolve;
      })
    );
    const onCancel = jest.fn();
    render(<AddItemForm onSubmit={onSubmit} onCancel={onCancel} />);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalledTimes(1);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Widget" },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "WDG-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();

    finishSubmission();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
    });
  });
});
