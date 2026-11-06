"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AddItemForm, type NewItem } from "@/components/AddItemForm";
import { ItemTable } from "@/components/ItemTable";
import {
  adjustStock,
  createItem,
  deleteItem,
  fetchItems,
  logout as revokeSession,
  type Item,
} from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";
import styles from "./page.module.css";

export default function DashboardPage() {
  const router = useRouter();
  const [token, setTokenState] = useState<string | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [query, setQuery] = useState("");

  const load = useCallback(async (t: string) => {
    const data = await fetchItems(t);
    setItems(data);
  }, []);

  useEffect(() => {
    let t: string | null;
    try {
      t = getToken();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication storage is unavailable");
      router.replace("/");
      setLoading(false);
      return;
    }
    if (!t) {
      router.replace("/");
      return;
    }
    setTokenState(t);
    load(t)
      .catch(() => {
        try {
          clearToken();
        } catch {
          // Continue redirecting even when browser storage is unavailable.
        }
        router.replace("/");
      })
      .finally(() => setLoading(false));
  }, [load, router]);

  async function handleAdjust(id: number, delta: number) {
    if (!token) return;
    setBusyId(id);
    setError("");
    try {
      const updated = await adjustStock(token, id, delta);
      setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Adjust failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(id: number) {
    if (!token) return;
    if (!confirm("Delete this item?")) return;
    setBusyId(id);
    setError("");
    try {
      await deleteItem(token, id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleCreate(body: NewItem) {
    if (!token) return;
    const created = await createItem(token, body);
    setItems((prev) => [...prev, created].sort((a, b) => a.name.localeCompare(b.name)));
    setAdding(false);
  }

  async function logout() {
    try {
      if (token) await revokeSession(token);
    } catch {
      // Clear the local session even if the server cannot be reached.
    } finally {
      try {
        clearToken();
      } catch {
        // Continue leaving the dashboard even when browser storage is unavailable.
      }
      router.push("/");
    }
  }

  const lowCount = items.filter((i) => i.low_stock).length;
  const totalUnits = items.reduce((sum, i) => sum + i.quantity, 0);
  const q = query.trim().toLowerCase();
  const visible = q
    ? items.filter((i) =>
        [i.name, i.sku, i.location].some((v) => v.toLowerCase().includes(q))
      )
    : items;

  return (
    <>
      <header className={styles.topbar}>
        <div className={styles.topbarInner}>
          <div className={styles.brand}>
            <span className={styles.logo} aria-hidden>
              ▦
            </span>
            Storage
          </div>
          <button type="button" className="ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </header>

      <main className={styles.page}>
        <h1>Inventory</h1>
        <p className={styles.muted}>
          See what you have, where it is, and what needs restocking.
        </p>

        {loading ? (
          <p className={styles.muted}>Loading…</p>
        ) : (
          <>
            <section className={styles.stats}>
              <div className={styles.stat}>
                <span>Products</span>
                <strong>{items.length}</strong>
              </div>
              <div className={styles.stat}>
                <span>Units in stock</span>
                <strong>{totalUnits}</strong>
              </div>
              <div className={styles.stat} data-warn={lowCount > 0 || undefined}>
                <span>Need restocking</span>
                <strong>{lowCount}</strong>
              </div>
            </section>

            <div className={styles.toolbar}>
              <input
                type="search"
                placeholder="Search by name, SKU or location…"
                aria-label="Search items"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              {!adding && (
                <button type="button" onClick={() => setAdding(true)}>
                  + Add item
                </button>
              )}
            </div>

            {adding && (
              <AddItemForm onSubmit={handleCreate} onCancel={() => setAdding(false)} />
            )}
            {error && <p className="error">{error}</p>}
            <ItemTable
              items={visible}
              onAdjust={handleAdjust}
              onDelete={handleDelete}
              busyId={busyId}
            />
          </>
        )}
      </main>
    </>
  );
}
