"use client";

import type { Item } from "@/lib/api";
import styles from "./ItemTable.module.css";

type Props = {
  items: Item[];
  onAdjust: (id: number, delta: number) => void;
  onDelete: (id: number) => void;
  busyId: number | null;
};

export function ItemTable({ items, onAdjust, onDelete, busyId }: Props) {
  if (items.length === 0) {
    return <p className={styles.empty}>No items in stock yet.</p>;
  }

  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Name</th>
            <th>Location</th>
            <th>Qty</th>
            <th>Min</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} data-low={item.low_stock || undefined}>
              <td className={styles.sku}>{item.sku}</td>
              <td>
                <div className={styles.name}>{item.name}</div>
                {item.description && (
                  <div className={styles.desc}>{item.description}</div>
                )}
              </td>
              <td>{item.location}</td>
              <td className={styles.qty}>{item.quantity}</td>
              <td>{item.min_stock}</td>
              <td>
                <span
                  className={
                    item.low_stock ? styles.badgeWarn : styles.badgeOk
                  }
                >
                  {item.low_stock ? "Low" : "OK"}
                </span>
              </td>
              <td>
                <div className={styles.actions}>
                  <button
                    type="button"
                    className="ghost"
                    disabled={busyId === item.id}
                    onClick={() => onAdjust(item.id, 1)}
                    aria-label={`Increase ${item.name}`}
                  >
                    +1
                  </button>
                  <button
                    type="button"
                    className="ghost"
                    disabled={busyId === item.id}
                    onClick={() => onAdjust(item.id, -1)}
                    aria-label={`Decrease ${item.name}`}
                  >
                    −1
                  </button>
                  <button
                    type="button"
                    className="danger"
                    disabled={busyId === item.id}
                    onClick={() => onDelete(item.id)}
                    aria-label={`Delete ${item.name}`}
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
