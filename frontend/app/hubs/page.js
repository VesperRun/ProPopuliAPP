"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Nav from "../../components/Nav";
import GateChallenge from "../../components/GateChallenge";
import VerifyBanner from "../../components/VerifyBanner";
import { authHref } from "../../lib/auth";
import { api, getToken } from "../../lib/api";
import { CONTENT_POLICY_MESSAGE, contentPolicyViolation } from "../../lib/contentPolicy";
import { normalizeSubpopSlug, subpopLabel, subpopPath } from "../../lib/subpop";

const SLUG_PATTERN = /^[a-z0-9-]+$/;

export default function HubsPage() {
  const router = useRouter();
  const [hubs, setHubs] = useState([]);
  const [error, setError] = useState("");
  const [authed, setAuthed] = useState(false);
  const [verified, setVerified] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [slug, setSlug] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [gate, setGate] = useState(null);

  const loadHubs = () => {
    api("/hubs")
      .then(setHubs)
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    loadHubs();
    const tok = getToken();
    setAuthed(!!tok);
    if (tok) {
      api("/me")
        .then((u) => setVerified(u.email_verified))
        .catch(() => setVerified(false));
    }
  }, []);

  async function createSubpop(e) {
    e.preventDefault();
    if (!getToken()) {
      router.push(authHref("/register", "/hubs"));
      return;
    }
    const normalized = normalizeSubpopSlug(slug);
    if (contentPolicyViolation(normalized, name, description)) {
      setError(CONTENT_POLICY_MESSAGE);
      return;
    }
    if (!SLUG_PATTERN.test(normalized)) {
      setError("Use the name only (e.g. intro → s\\intro). Letters, numbers, hyphens, 2–32 chars.");
      return;
    }
    setCreating(true);
    setError("");
    setGate(null);
    try {
      const hub = await api("/hubs", {
        method: "POST",
        body: JSON.stringify({
          slug: normalized,
          name: name.trim(),
          description: description.trim(),
        }),
      });
      router.push(subpopPath(hub.slug));
    } catch (err) {
      if (err.status === 422 && err.payload?.detail) {
        const d = err.payload.detail;
        setGate(typeof d === "object" ? d : { detail: String(d) });
      } else {
        setError(err.message);
      }
      setCreating(false);
    }
  }

  return (
    <main className="container">
      <Nav />
      <h2>Subpops</h2>
      <p className="meta" style={{ marginTop: "-0.5rem" }}>
        Niche communities — symbolically <strong>s\name</strong>.
      </p>

      {authed && <VerifyBanner verified={verified} />}

      {authed && verified ? (
        <section className="card" style={{ marginBottom: "1rem" }}>
          {!showCreate ? (
            <button type="button" className="btn" onClick={() => setShowCreate(true)}>
              Create subpop
            </button>
          ) : (
            <form onSubmit={createSubpop}>
              <h3 style={{ marginTop: 0 }}>New subpop</h3>
              <label className="meta" htmlFor="subpop-slug">
                Name slug — we add s\ (
                {normalizeSubpopSlug(slug) && SLUG_PATTERN.test(normalizeSubpopSlug(slug))
                  ? subpopLabel(normalizeSubpopSlug(slug))
                  : "s\\intro"}
                )
              </label>
              <input
                id="subpop-slug"
                className="input"
                placeholder="intro"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                minLength={2}
                maxLength={32}
                required
              />
              <input
                className="input"
                style={{ marginTop: "0.5rem" }}
                placeholder="Display name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                minLength={2}
                maxLength={128}
                required
              />
              <textarea
                className="textarea"
                style={{ marginTop: "0.5rem" }}
                placeholder="Short description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={512}
              />
              <GateChallenge gate={gate} />
              <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem" }}>
                <button className="btn" type="submit" disabled={creating}>
                  {creating ? "Creating…" : "Create"}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowCreate(false);
                    setError("");
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </section>
      ) : !authed ? (
        <p className="meta">
          <Link href={authHref("/register", "/hubs")}>Sign up</Link> to create your own subpop.
        </p>
      ) : null}

      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      {hubs.map((hub) => (
        <Link key={hub.id} href={subpopPath(hub.slug)} className="card" style={{ display: "block" }}>
          <strong>{subpopLabel(hub.slug)}</strong>
          <div>{hub.name}</div>
          <p className="meta" style={{ marginBottom: 0 }}>
            {hub.description}
          </p>
        </Link>
      ))}
    </main>
  );
}
