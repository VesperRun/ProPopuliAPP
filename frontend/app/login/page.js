"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Nav from "../../components/Nav";
import { api, setToken } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
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
        <h2 style={{ marginTop: 0 }}>Log in</h2>
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
          type="password"
          placeholder="Password"
          style={{ marginTop: "0.5rem" }}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p style={{ color: "#b00020" }}>{error}</p>}
        <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
          Log in
        </button>
        <p className="meta">
          No account? <Link href="/register">Register</Link>
        </p>
      </form>
    </main>
  );
}
