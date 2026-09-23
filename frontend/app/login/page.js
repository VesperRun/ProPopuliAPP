"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import Nav from "../../components/Nav";
import PasswordInput from "../../components/PasswordInput";
import { safeReturnPath } from "../../lib/auth";
import { api, setToken } from "../../lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = safeReturnPath(searchParams.get("next"));
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
      router.push(next);
    } catch (err) {
      setError(err.message);
    }
  }

  const registerHref = next === "/hubs" ? "/register" : `/register?next=${encodeURIComponent(next)}`;

  return (
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
      <PasswordInput
        id="login-password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <div className="login-forgot">
        <Link href="/forgot-password">Forgot your password?</Link>
      </div>
      {error && <p style={{ color: "#b00020", marginTop: "0.5rem" }}>{error}</p>}
      <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
        Log in
      </button>
      <p className="meta">
        No account? <Link href={registerHref}>Sign up</Link>
      </p>
    </form>
  );
}

export default function LoginPage() {
  return (
    <main className="container">
      <Nav />
      <Suspense fallback={<p className="meta">Loading…</p>}>
        <LoginForm />
      </Suspense>
    </main>
  );
}
