"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import Nav from "../../components/Nav";
import PasswordInput from "../../components/PasswordInput";
import { api } from "../../lib/api";

function ResetForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, password }),
      });
      setMessage(data.message);
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!token) {
    return (
      <div className="card" style={{ maxWidth: 420 }}>
        <h2 style={{ marginTop: 0 }}>Reset password</h2>
        <p style={{ color: "#b00020" }}>Missing reset link. Use forgot password to request a new one.</p>
        <Link href="/forgot-password">Forgot password</Link>
      </div>
    );
  }

  return (
    <form className="card" onSubmit={onSubmit} style={{ maxWidth: 420 }}>
      <h2 style={{ marginTop: 0 }}>Choose a new password</h2>
      <PasswordInput
        id="reset-password"
        placeholder="New password (8+ characters)"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      {message && <p style={{ color: "#0a6b0a" }}>{message}</p>}
      <button className="btn" type="submit" style={{ marginTop: "0.75rem" }} disabled={!!message}>
        Update password
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <main className="container">
      <Nav />
      <Suspense fallback={<p className="meta">Loading…</p>}>
        <ResetForm />
      </Suspense>
    </main>
  );
}
