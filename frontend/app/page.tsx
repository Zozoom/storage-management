"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { hasSession } from "@/lib/auth";
import styles from "./page.module.css";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    hasSession().then((active) => {
      if (active) router.replace("/dashboard");
    }).catch(() => {});
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.wrap}>
      <section className={styles.panel}>
        <div className={styles.logo} aria-hidden>
          ▦
        </div>
        <h1>Welcome back</h1>
        <p className={styles.sub}>Sign in to manage your warehouse stock.</p>
        <form onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>
          <button type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
        <div className={styles.demo}>
          Try a demo account:
          <div className={styles.demoRow}>
            {["admin", "clerk"].map((u) => (
              <button
                key={u}
                type="button"
                className="ghost"
                onClick={() => {
                  setUsername(u);
                  setPassword(`${u}123`);
                }}
              >
                {u}
              </button>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
