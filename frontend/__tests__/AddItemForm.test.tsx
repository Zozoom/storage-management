import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { AddItemForm } from "@/components/AddItemForm";

describe("AddItemForm", () => {
  it("submits trimmed values, applies defaults, and omits an empty description", async () => {
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
    fireEvent.change(screen.getByLabelText("Quantity"), {
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
        quantity: 0,
        location: "A-01",
        min_stock: 5,
      })
    );
    expect(onSubmit.mock.calls[0][0]).not.toHaveProperty("description");
  });

  it("shows the saving state and disables submission while the callback is pending", async () => {
    let finish!: () => void;
    const pending = new Promise<void>((resolve) => {
      finish = resolve;
    });
    const onSubmit = jest.fn(() => pending);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    const savingButton = screen.getByRole("button", { name: "Saving…" });
    expect(savingButton).toBeDisabled();
    expect(onSubmit).toHaveBeenCalledTimes(1);

    await act(async () => {
      finish();
      await pending;
    });

    expect(screen.getByRole("button", { name: "Save item" })).toBeEnabled();
  });

  it("displays callback errors and allows retry", async () => {
    const onSubmit = jest
      .fn()
      .mockRejectedValueOnce(new Error("Could not save item"))
      .mockResolvedValueOnce(undefined);
    render(<AddItemForm onSubmit={onSubmit} onCancel={jest.fn()} />);

    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    expect(await screen.findByText("Could not save item")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Save item" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(screen.queryByText("Could not save item")).not.toBeInTheDocument()
    );
  });

  it("invokes the cancel callback", () => {
    const onCancel = jest.fn();
    render(<AddItemForm onSubmit={jest.fn()} onCancel={onCancel} />);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCancel).toHaveBeenCalledTimes(1);
  });
});
