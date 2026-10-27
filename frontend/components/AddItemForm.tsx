"use client";

import { FormEvent, useState } from "react";
import styles from "./AddItemForm.module.css";

export type NewItem = {
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  location: string;
  min_stock: number;
};

type Props = {
  onSubmit: (item: NewItem) => Promise<void>;
};

export function AddItemForm({ onSubmit }: Props) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const fd = new FormData(e.currentTarget);
    try {
      await onSubmit({
        sku: String(fd.get("sku")).trim(),
        name: String(fd.get("name")).trim(),
        description: String(fd.get("description") || "").trim() || undefined,
        quantity: Number(fd.get("quantity") || 0),
        location: String(fd.get("location") || "A-01").trim(),
        min_stock: Number(fd.get("min_stock") || 5),
      });
      e.currentTarget.reset();
      setOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add item");
    } finally {
      setLoading(false);
    }
  }

  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)}>
        Add item
      </button>
    );
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <div className={styles.grid}>
        <div className="field">
          <label htmlFor="sku">SKU</label>
          <input id="sku" name="sku" required />
        </div>
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" required />
        </div>
        <div className="field">
          <label htmlFor="quantity">Quantity</label>
          <input id="quantity" name="quantity" type="number" min={0} defaultValue={0} />
        </div>
        <div className="field">
          <label htmlFor="location">Location</label>
          <input id="location" name="location" defaultValue="A-01" />
        </div>
        <div className="field">
          <label htmlFor="min_stock">Min stock</label>
          <input id="min_stock" name="min_stock" type="number" min={0} defaultValue={5} />
        </div>
        <div className="field">
          <label htmlFor="description">Description</label>
          <input id="description" name="description" />
        </div>
      </div>
      <div className={styles.row}>
        <button type="submit" disabled={loading}>
          {loading ? "Saving…" : "Save item"}
        </button>
        <button type="button" className="ghost" onClick={() => setOpen(false)}>
          Cancel
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
