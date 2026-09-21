"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { api } from "../../lib/api";

export default function ContactPage() {
  const [adminEmail, setAdminEmail] = useState(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/public/contact")
      .then((data) => {
        setAdminEmail(data.admin_email);
        setLoaded(true);
      })
      .catch((e) => {
        setError(e.message);
        setLoaded(true);
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
        {error && <p style={{ color: "#b00020" }}>{error}</p>}
        {loaded && !error && adminEmail && (
          <p style={{ marginBottom: 0 }}>
            <a className="btn" href={`mailto:${encodeURIComponent(adminEmail)}`}>
              Email admin
            </a>
            <span className="meta" style={{ display: "block", marginTop: "0.75rem" }}>
              {adminEmail}
            </span>
          </p>
        )}
        {loaded && !error && !adminEmail && (
          <p className="meta" style={{ marginBottom: 0 }}>
            Admin contact is not configured yet. Set <code>CONTACT_ADMIN_EMAIL</code> in backend{" "}
            <code>.env</code> and restart the API.
          </p>
        )}
      </section>
      <p className="meta" style={{ marginTop: "1rem" }}>
        <Link href="/">Home</Link>
      </p>
    </main>
  );
}
