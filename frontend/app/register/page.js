"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Nav from "../../components/Nav";
import { api, setToken } from "../../lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [handle, setHandle] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, handle, password }),
      });
      setToken(data.access_token);
      router.push("/hubs");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="container">
      <Nav />
      <form className="card" onSubmit={onSubmit} style={{ maxWidth: 420 }}>
        <h2 style={{ marginTop: 0 }}>Register</h2>
        <p className="meta">Public handle only — no legal names.</p>
        <input
          className="input"
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="input"
          placeholder="Handle"
          style={{ marginTop: "0.5rem" }}
          value={handle}
          onChange={(e) => setHandle(e.target.value)}
          required
        />
        <input
          className="input"
          type="password"
          placeholder="Password (8+ chars)"
          style={{ marginTop: "0.5rem" }}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p style={{ color: "#b00020" }}>{error}</p>}
        <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
          Create account
        </button>
        <p className="meta">
          Already registered? <Link href="/login">Log in</Link>
        </p>
      </form>
    </main>
  );
}
