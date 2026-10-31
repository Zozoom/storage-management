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
  onCancel: () => void;
};

export function AddItemForm({ onSubmit, onCancel }: Props) {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add item");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <h2 className={styles.title}>New item</h2>
      <div className={styles.grid}>
        <div className="field">
          <label htmlFor="name">Name</label>
          <input id="name" name="name" placeholder="e.g. Shipping box" required />
        </div>
        <div className="field">
          <label htmlFor="sku">SKU</label>
          <input id="sku" name="sku" placeholder="e.g. BOX-M" required />
          <p className="hint">Unique product code.</p>
        </div>
        <div className="field">
          <label htmlFor="quantity">Quantity</label>
          <input id="quantity" name="quantity" type="number" min={0} defaultValue={0} />
        </div>
        <div className="field">
          <label htmlFor="location">Location</label>
          <input id="location" name="location" defaultValue="A-01" />
          <p className="hint">Shelf or bin, e.g. A-01.</p>
        </div>
        <div className="field">
          <label htmlFor="min_stock">Restock below</label>
          <input id="min_stock" name="min_stock" type="number" min={0} defaultValue={5} />
          <p className="hint">Flags the item when stock drops under this.</p>
        </div>
        <div className="field">
          <label htmlFor="description">Description (optional)</label>
          <input id="description" name="description" />
        </div>
      </div>
      <div className={styles.row}>
        <button type="button" className="ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" disabled={loading}>
          {loading ? "Saving…" : "Save item"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
