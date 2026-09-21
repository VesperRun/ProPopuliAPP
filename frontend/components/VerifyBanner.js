"use client";

import Link from "next/link";
import { useState } from "react";
import { api } from "../lib/api";

export default function VerifyBanner({ verified }) {
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  if (verified) return null;

  async function resend() {
    setErr("");
    setMsg("");
    try {
      const data = await api("/auth/resend-verification", { method: "POST" });
      setMsg(data.message);
    } catch (e) {
      setErr(e.message);
    }
  }

  return (
    <div className="card" style={{ background: "#fff8e6", borderColor: "#e6d9a8" }}>
      <strong>Verify your email</strong>
      <p style={{ margin: "0.5rem 0", color: "#444" }}>
        You can browse subpops and read threads. Posting, replies, and creating subpops unlock after you confirm your email.
      </p>
      <button type="button" className="btn btn-secondary" onClick={resend}>
        Resend verification email
      </button>
      <Link href="/verify-email" style={{ marginLeft: "0.75rem" }}>
        I have a link
      </Link>
      {msg && <p className="meta" style={{ marginTop: "0.75rem", marginBottom: 0 }}>{msg}</p>}
      {err && <p style={{ color: "#b00020", marginBottom: 0 }}>{err}</p>}
    </div>
  );
}
