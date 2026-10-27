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

  const load = useCallback(async (t: string) => {
    const data = await fetchItems(t);
    setItems(data);
  }, []);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.replace("/");
      return;
    }
    setTokenState(t);
    load(t)
      .catch(() => {
        clearToken();
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
  }

  function logout() {
    clearToken();
    router.push("/");
  }

  const lowCount = items.filter((i) => i.low_stock).length;

  if (loading) {
    return (
      <main className={styles.page}>
        <p className={styles.muted}>Loading…</p>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.brand}>Storage</p>
          <h1>Stock inventory</h1>
          <p className={styles.muted}>
            {items.length} items
            {lowCount > 0 ? ` · ${lowCount} low stock` : ""}
          </p>
        </div>
        <button type="button" className="ghost" onClick={logout}>
          Log out
        </button>
      </header>

      <AddItemForm onSubmit={handleCreate} />
      {error && <p className="error">{error}</p>}
      <ItemTable
        items={items}
        onAdjust={handleAdjust}
        onDelete={handleDelete}
        busyId={busyId}
      />
    </main>
  );
}
