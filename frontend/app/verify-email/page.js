"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { api } from "../../lib/api";

function VerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");
  const [status, setStatus] = useState(token ? "working" : "pending");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) return;
    api("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
      .then((data) => {
        setStatus("ok");
        setMessage(data.message);
      })
      .catch((e) => {
        setStatus("error");
        setMessage(e.message);
      });
  }, [token]);

  return (
    <div className="card" style={{ maxWidth: 480 }}>
      <h2 style={{ marginTop: 0 }}>Email verification</h2>
      {!token && (
        <>
          <p style={{ color: "#444" }}>
            Open the link we sent to your inbox. If Resend is not configured, check the backend terminal for a dev link.
          </p>
          <Link href="/hubs">Back to hubs</Link>
        </>
      )}
      {token && status === "working" && <p className="meta">Verifying…</p>}
      {token && status === "ok" && (
        <>
          <p style={{ color: "#0a6b0a" }}>{message}</p>
          <button type="button" className="btn" onClick={() => router.push("/hubs")}>
            Continue to hubs
          </button>
        </>
      )}
      {token && status === "error" && (
        <>
          <p style={{ color: "#b00020" }}>{message}</p>
          <Link href="/hubs">Back to hubs</Link>
        </>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <main className="container">
      <Nav />
      <Suspense fallback={<p className="meta">Loading…</p>}>
        <VerifyContent />
      </Suspense>
    </main>
  );
}
