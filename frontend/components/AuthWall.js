"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { authHref } from "../lib/auth";

export default function AuthWall({ title = "Join to participate", message }) {
  const pathname = usePathname();
  const defaultMessage =
    "You can read hubs and threads without an account. Sign up to post and reply (Reframing Gate applies to replies).";

  return (
    <div className="card auth-wall">
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <p style={{ margin: "0.5rem 0 1rem", color: "#444", lineHeight: 1.5 }}>{message || defaultMessage}</p>
      <div className="auth-wall-actions">
        <Link href={authHref("/register", pathname)} className="btn">
          Sign up
        </Link>
        <Link href={authHref("/login", pathname)} className="btn btn-secondary">
          Log in
        </Link>
      </div>
    </div>
  );
}
