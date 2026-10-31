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
    return <p className={styles.empty}>No items found.</p>;
  }

  return (
    <div className={styles.wrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Item</th>
            <th>Location</th>
            <th>Quantity</th>
            <th>Status</th>
            <th aria-label="Actions" />
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const busy = busyId === item.id;
            return (
              <tr key={item.id}>
                <td>
                  <div className={styles.name}>{item.name}</div>
                  <div className={styles.sku}>{item.sku}</div>
                  {item.description && (
                    <div className={styles.desc}>{item.description}</div>
                  )}
                </td>
                <td>
                  <span className={styles.loc}>{item.location}</span>
                </td>
                <td>
                  <div className={styles.stepper}>
                    <button
                      type="button"
                      className="ghost"
                      disabled={busy || item.quantity === 0}
                      onClick={() => onAdjust(item.id, -1)}
                      aria-label={`Decrease ${item.name}`}
                    >
                      −
                    </button>
                    <span className={styles.qty}>{item.quantity}</span>
                    <button
                      type="button"
                      className="ghost"
                      disabled={busy}
                      onClick={() => onAdjust(item.id, 1)}
                      aria-label={`Increase ${item.name}`}
                    >
                      +
                    </button>
                  </div>
                  <div className={styles.desc}>Restock below {item.min_stock}</div>
                </td>
                <td>
                  <span className={item.low_stock ? styles.badgeWarn : styles.badgeOk}>
                    {item.low_stock ? "Low stock" : "In stock"}
                  </span>
                </td>
                <td className={styles.right}>
                  <button
                    type="button"
                    className="danger"
                    disabled={busy}
                    onClick={() => onDelete(item.id)}
                    aria-label={`Delete ${item.name}`}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
