"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import Nav from "../../components/Nav";
import { authHref } from "../../lib/auth";
import { api, getToken } from "../../lib/api";
import { DEFAULT_ADMIN_EMAIL } from "../../lib/contact";
import { composeUrlForUserEmail } from "../../lib/mailCompose";

export default function ContactPage() {
  const [adminEmail, setAdminEmail] = useState(DEFAULT_ADMIN_EMAIL);
  const [userEmail, setUserEmail] = useState(null);
  /** pending = same on server and client until mount (avoids hydration mismatch) */
  const [authState, setAuthState] = useState("pending");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api("/public/contact")
      .then((data) => {
        if (data.admin_email) setAdminEmail(data.admin_email);
      })
      .catch(() => {});

    const tok = getToken();
    if (!tok) {
      setAuthState("guest");
      return;
    }
    api("/me")
      .then((u) => {
        setUserEmail(u.email);
        setAuthState("ready");
      })
      .catch(() => setAuthState("guest"));
  }, []);

  const composeUrl = useMemo(() => {
    if (!userEmail) return null;
    return composeUrlForUserEmail(userEmail, {
      to: adminEmail,
      subject: "ProPopuli contact",
    });
  }, [userEmail, adminEmail]);

  function openCompose() {
    if (!composeUrl) return;
    window.open(composeUrl, "_blank", "noopener,noreferrer");
  }

  async function copyAddress() {
    try {
      await navigator.clipboard.writeText(adminEmail);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <main className="container">
      <Nav />
      <h1 style={{ marginTop: 0 }}>Contact ProPopuli admin</h1>
      <section className="card" style={{ maxWidth: "36rem" }}>
        <p style={{ color: "#444", lineHeight: 1.55, marginTop: 0 }}>
          Feedback, suggestions, abuse reports, appeals, or platform questions — reach the admin directly.
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
          {authState === "pending" && (
            <button type="button" className="btn" disabled>
              Email admin
            </button>
          )}
          {authState === "guest" && (
            <Link className="btn" href={authHref("/login", "/contact")}>
              Log in to email admin
            </Link>
          )}
          {authState === "ready" && composeUrl && (
            <button type="button" className="btn" onClick={openCompose}>
              Email admin
            </button>
          )}
          {authState === "ready" && !composeUrl && (
            <span className="meta">Use copy — your email provider isn&apos;t linked for one-click compose.</span>
          )}
          <button type="button" className="btn btn-secondary" onClick={copyAddress}>
            {copied ? "Copied" : "Copy address"}
          </button>
        </div>
        <p className="meta" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          {adminEmail}
        </p>
        {authState === "ready" && composeUrl && userEmail && (
          <p className="meta" style={{ marginTop: "0.5rem", marginBottom: 0 }}>
            Opens compose in the webmail for the address you signed up with ({userEmail}).
          </p>
        )}
      </section>
      <p className="meta" style={{ marginTop: "1rem" }}>
        <Link href="/">Home</Link>
      </p>
    </main>
  );
}
