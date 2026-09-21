"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { api } from "../../lib/api";
import { DEFAULT_ADMIN_EMAIL } from "../../lib/contact";

export default function ContactPage() {
  const [adminEmail, setAdminEmail] = useState(DEFAULT_ADMIN_EMAIL);

  useEffect(() => {
    api("/public/contact")
      .then((data) => {
        if (data.admin_email) setAdminEmail(data.admin_email);
      })
      .catch(() => {
        /* Keep DEFAULT_ADMIN_EMAIL if API is down or route not deployed yet */
      });
  }, []);

  return (
    <main className="container">
      <Nav />
      <h1 style={{ marginTop: 0 }}>Contact ProPopuli admin</h1>
      <section className="card" style={{ maxWidth: "36rem" }}>
        <p style={{ color: "#444", lineHeight: 1.55, marginTop: 0 }}>
          Feedback, suggestions, abuse reports, appeals, or platform questions — email the admin directly.
        </p>
        <p style={{ marginBottom: 0 }}>
          <a className="btn" href={`mailto:${encodeURIComponent(adminEmail)}`}>
            Email admin
          </a>
          <span className="meta" style={{ display: "block", marginTop: "0.75rem" }}>
            {adminEmail}
          </span>
        </p>
      </section>
      <p className="meta" style={{ marginTop: "1rem" }}>
        <Link href="/">Home</Link>
      </p>
    </main>
  );
}
