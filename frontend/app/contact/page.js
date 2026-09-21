"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { authHref } from "../../lib/auth";
import { api, getToken } from "../../lib/api";
import { DEFAULT_ADMIN_EMAIL } from "../../lib/contact";
import { composeUrlForUserEmail } from "../../lib/mailCompose";

export default function ContactPage() {
  const [adminEmail, setAdminEmail] = useState(DEFAULT_ADMIN_EMAIL);
  const [userEmail, setUserEmail] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api("/public/contact")
      .then((data) => {
        if (data.admin_email) setAdminEmail(data.admin_email);
      })
      .catch(() => {});

    if (getToken()) {
      api("/me")
        .then((u) => setUserEmail(u.email))
        .catch(() => setUserEmail(null));
    }
  }, []);

  const composeUrl =
    userEmail &&
    composeUrlForUserEmail(userEmail, {
      to: adminEmail,
      subject: "ProPopuli contact",
    });

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
          {composeUrl ? (
            <button type="button" className="btn" onClick={openCompose}>
              Email admin
            </button>
          ) : getToken() ? (
            <p className="meta" style={{ margin: 0 }}>
              We don&apos;t recognize your email provider for one-click compose. Use copy below.
            </p>
          ) : (
            <Link className="btn" href={authHref("/login", "/contact")}>
              Log in to email admin
            </Link>
          )}
          <button type="button" className="btn btn-secondary" onClick={copyAddress}>
            {copied ? "Copied" : "Copy address"}
          </button>
        </div>
        <p className="meta" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
          {adminEmail}
        </p>
        {composeUrl && (
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
