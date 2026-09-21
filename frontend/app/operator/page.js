"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import { api, getToken } from "../../lib/api";
import { subpopLabel } from "../../lib/subpop";

export default function OperatorPage() {
  const router = useRouter();
  const [allowed, setAllowed] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [subpopSlug, setSubpopSlug] = useState("");
  const [userHandle, setUserHandle] = useState("");
  const [modAction, setModAction] = useState("timeout");
  const [timeoutHours, setTimeoutHours] = useState("24");
  const [modNote, setModNote] = useState("");

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login?next=%2Foperator");
      return;
    }
    api("/me")
      .then((u) => {
        if (!u.is_operator) {
          router.replace("/hubs");
          return;
        }
        setAllowed(true);
      })
      .catch((e) => setError(e.message));
  }, [router]);

  async function deleteSubpop(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    const slug = subpopSlug.trim().toLowerCase();
    if (!slug) return;
    if (!window.confirm(`Delete ${subpopLabel(slug)} and all its posts? This cannot be undone.`)) return;
    try {
      const data = await api(`/operator/subpops/${encodeURIComponent(slug)}`, { method: "DELETE" });
      setMessage(data.message);
      setSubpopSlug("");
    } catch (err) {
      setError(err.message);
    }
  }

  async function moderateUser(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    const handle = userHandle.trim();
    if (!handle) return;
    const body = {
      action: modAction,
      note: modNote.trim(),
    };
    if (modAction === "timeout") {
      body.hours = parseInt(timeoutHours, 10) || 24;
    }
    try {
      const data = await api(`/operator/users/${encodeURIComponent(handle)}/moderate`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      setMessage(data.message);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!allowed) {
    return (
      <main className="container">
        <Nav />
        {error && <p style={{ color: "#b00020" }}>{error}</p>}
      </main>
    );
  }

  return (
    <main className="container">
      <Nav />
      <h2>Operator</h2>
      <p className="meta">
        Platform sovereignty — delete subpops, bar accounts, timeouts, pardon. Identity is bound to{" "}
        <code>OPERATOR_HANDLES</code> / <code>OPERATOR_EMAILS</code> in backend <code>.env</code> (not in git).
      </p>

      {message && <p style={{ color: "#0a6b0a" }}>{message}</p>}
      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      <form className="card" onSubmit={deleteSubpop}>
        <h3 style={{ marginTop: 0 }}>Delete subpop</h3>
        <input
          className="input"
          placeholder="slug (e.g. spam-niche)"
          value={subpopSlug}
          onChange={(e) => setSubpopSlug(e.target.value)}
        />
        <button className="btn" type="submit" style={{ marginTop: "0.75rem", background: "#8b0000" }}>
          Delete subpop
        </button>
      </form>

      <form className="card" onSubmit={moderateUser}>
        <h3 style={{ marginTop: 0 }}>Moderate account</h3>
        <input
          className="input"
          placeholder="Handle (without @)"
          value={userHandle}
          onChange={(e) => setUserHandle(e.target.value)}
          required
        />
        <select
          className="input"
          style={{ marginTop: "0.5rem" }}
          value={modAction}
          onChange={(e) => setModAction(e.target.value)}
        >
          <option value="timeout">Timeout (read-only)</option>
          <option value="bar">Bar (permanent — cannot log in)</option>
          <option value="pardon">Pardon (clear bar / timeout)</option>
        </select>
        {modAction === "timeout" && (
          <input
            className="input"
            style={{ marginTop: "0.5rem" }}
            type="number"
            min={1}
            max={8760}
            value={timeoutHours}
            onChange={(e) => setTimeoutHours(e.target.value)}
            placeholder="Hours"
          />
        )}
        <textarea
          className="textarea"
          style={{ marginTop: "0.5rem" }}
          placeholder="Internal note (optional)"
          value={modNote}
          onChange={(e) => setModNote(e.target.value)}
          maxLength={512}
        />
        <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
          Apply
        </button>
      </form>

      <p className="meta">
        <Link href="/hubs">Back to subpops</Link>
      </p>
    </main>
  );
}
