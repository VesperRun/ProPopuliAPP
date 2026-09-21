"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, clearToken, getToken } from "../lib/api";

export default function Nav() {
  const [handle, setHandle] = useState(null);
  const [verified, setVerified] = useState(true);

  useEffect(() => {
    if (!getToken()) return;
    api("/me")
      .then((u) => {
        setHandle(u.handle);
        setVerified(u.email_verified);
      })
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
          <span className="meta">
            @{handle}
            {!verified && " · unverified"}
          </span>
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
        <div className="nav-auth" style={{ marginLeft: "auto" }}>
          <Link href="/login">Log in</Link>
          <Link href="/register" className="btn btn-nav-signup">
            Sign up
          </Link>
        </div>
      )}
    </nav>
  );
}
