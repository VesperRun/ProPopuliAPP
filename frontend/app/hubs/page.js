"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { api } from "../../lib/api";

export default function HubsPage() {
  const [hubs, setHubs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/hubs")
      .then(setHubs)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <main className="container">
      <Nav />
      <h2>Hubs</h2>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      {hubs.map((hub) => (
        <Link key={hub.id} href={`/h/${hub.slug}`} className="card" style={{ display: "block" }}>
          <strong>h/{hub.slug}</strong>
          <div>{hub.name}</div>
          <p className="meta" style={{ marginBottom: 0 }}>
            {hub.description}
          </p>
        </Link>
      ))}
    </main>
  );
}
