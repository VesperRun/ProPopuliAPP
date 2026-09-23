"use client";

import Link from "next/link";
import { useState } from "react";
import Nav from "../../components/Nav";
import { api } from "../../lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const data = await api("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setMessage(data.message);
      setSent(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="container">
      <Nav />
      <form className="card" onSubmit={onSubmit} style={{ maxWidth: 420 }}>
        <h2 style={{ marginTop: 0 }}>Forgot password</h2>
        <p className="meta" style={{ lineHeight: 1.5 }}>
          Enter your account email. We will send a link to choose a new password.
        </p>
        {!sent && (
          <>
            <input
              className="input"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {error && <p style={{ color: "#b00020" }}>{error}</p>}
            <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
              Send reset link
            </button>
          </>
        )}
        {message && <p style={{ color: "#0a6b0a" }}>{message}</p>}
        <p className="meta" style={{ marginBottom: 0 }}>
          <Link href="/login">Back to log in</Link>
        </p>
      </form>
    </main>
  );
}
