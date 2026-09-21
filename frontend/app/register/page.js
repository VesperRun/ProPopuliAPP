"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import Nav from "../../components/Nav";
import PasswordInput from "../../components/PasswordInput";
import { safeReturnPath } from "../../lib/auth";
import { api, setToken } from "../../lib/api";

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = safeReturnPath(searchParams.get("next"));
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
      router.push(next === "/hubs" ? "/verify-email" : next);
    } catch (err) {
      setError(err.message);
    }
  }

  const loginHref = next === "/hubs" ? "/login" : `/login?next=${encodeURIComponent(next)}`;

  return (
    <form className="card" onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h2 style={{ marginTop: 0 }}>Create account</h2>
      <p className="meta" style={{ lineHeight: 1.5 }}>
        Your <strong>handle</strong> is public on posts and replies. Your <strong>email</strong> stays private and
        anchors one account — no legal name required.
      </p>
      <label className="meta" htmlFor="reg-email">
        Email (private)
      </label>
      <input
        id="reg-email"
        className="input"
        type="email"
        placeholder="you@example.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <label className="meta" htmlFor="reg-handle" style={{ display: "block", marginTop: "0.75rem" }}>
        Handle (public)
      </label>
      <input
        id="reg-handle"
        className="input"
        placeholder="your_handle"
        value={handle}
        onChange={(e) => setHandle(e.target.value)}
        required
      />
      <label className="meta" htmlFor="reg-password" style={{ display: "block", marginTop: "0.75rem" }}>
        Password
      </label>
      <PasswordInput
        id="reg-password"
        placeholder="8+ characters"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
        Sign up
      </button>
      <p className="meta">
        Already have an account? <Link href={loginHref}>Log in</Link>
      </p>
    </form>
  );
}

export default function RegisterPage() {
  return (
    <main className="container">
      <Nav />
      <Suspense fallback={<p className="meta">Loading…</p>}>
        <RegisterForm />
      </Suspense>
    </main>
  );
}
