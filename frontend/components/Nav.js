"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, clearToken, getToken } from "../lib/api";

export default function Nav() {
  const [handle, setHandle] = useState(null);

  useEffect(() => {
    if (!getToken()) return;
    api("/me")
      .then((u) => setHandle(u.handle))
      .catch(() => clearToken());
  }, []);

  return (
    <nav className="nav">
      <Link href="/">
        <strong>ProPopuli</strong>
      </Link>
      <Link href="/hubs">Hubs</Link>
      {handle ? (
        <>
          <span className="meta">@{handle}</span>
          <button
            className="btn"
            style={{ marginLeft: "auto", background: "#444" }}
            onClick={() => {
              clearToken();
              window.location.href = "/login";
            }}
          >
            Log out
          </button>
        </>
      ) : (
        <Link href="/login" style={{ marginLeft: "auto" }}>
          Log in
        </Link>
      )}
    </nav>
  );
}
