import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  function fillRequiredFields() {
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "  Shipping box  " },
    });
    fireEvent.change(screen.getByLabelText("SKU"), {
      target: { value: "  BOX-M  " },
    });
  }

  it("trims fields and passes optional description and numeric values to onSubmit", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fillRequiredFields();
    fireEvent.change(screen.getByLabelText("Description (optional)"), {
      target: { value: "  " },
    });
    fireEvent.change(screen.getByLabelText("Quantity"), {
      target: { value: "12" },
    });
    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "  B-02  " },
    });
    fireEvent.change(screen.getByLabelText("Restock below"), {
      target: { value: "3" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "BOX-M",
        name: "Shipping box",
        description: undefined,
        quantity: 12,
        location: "B-02",
        min_stock: 3,
      })
    );
  });

  it("uses numeric and location defaults for empty fields", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fillRequiredFields();
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

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        sku: "BOX-M",
        name: "Shipping box",
        description: undefined,
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    );
  });

  it("shows a rejected submission error and clears the loading state", async () => {
    let rejectSubmission!: (reason: Error) => void;
    const onSubmit = jest.fn(
      () =>
        new Promise<void>((_resolve, reject) => {
          rejectSubmission = reject;
        })
    );
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);
    fillRequiredFields();

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));
    expect(screen.getByRole("button", { name: "Saving…" }).disabled).toBe(true);

    rejectSubmission(new Error("Could not save item"));

    expect(await screen.findByText("Could not save item")).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Save item" }).disabled).toBe(false);
    });
  });

  it("invokes onCancel when canceled", () => {
    const onCancel = jest.fn();
    render(<AddItemForm onSubmit={jest.fn()} onCancel={onCancel} />);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
