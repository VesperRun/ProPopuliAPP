"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AuthWall from "./AuthWall";
import Nav from "./Nav";
import VerifyBanner from "./VerifyBanner";
import { authHref } from "../lib/auth";
import { CONTENT_POLICY_MESSAGE, contentPolicyViolation } from "../lib/contentPolicy";
import { api, getToken } from "../lib/api";
import { subpopLabel, subpopPath } from "../lib/subpop";

export default function SubpopPage() {
  const { slug } = useParams();
  const router = useRouter();
  const [hub, setHub] = useState(null);
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [error, setError] = useState("");
  const [authed, setAuthed] = useState(false);
  const [verified, setVerified] = useState(true);
  const [isOperator, setIsOperator] = useState(false);

  const load = () => {
    Promise.all([api(`/hubs/${slug}`), api(`/hubs/${slug}/posts`)])
      .then(([h, list]) => {
        setHub(h);
        setPosts(list);
      })
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    const tok = getToken();
    setAuthed(!!tok);
    if (tok) {
      api("/me")
        .then((u) => {
          setVerified(u.email_verified);
          setIsOperator(!!u.is_operator);
        })
        .catch(() => setVerified(true));
    }
    if (slug) load();
  }, [slug]);

  async function deleteSubpop() {
    if (!window.confirm(`Delete ${subpopLabel(slug)} and all threads? Permanent.`)) return;
    setError("");
    try {
      await api(`/operator/subpops/${encodeURIComponent(slug)}`, { method: "DELETE" });
      router.push("/hubs");
    } catch (err) {
      setError(err.message);
    }
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!getToken()) {
      router.push(authHref("/register", subpopPath(slug)));
      return;
    }
    setError("");
    if (contentPolicyViolation(title, body)) {
      setError(CONTENT_POLICY_MESSAGE);
      return;
    }
    try {
      const post = await api(`/hubs/${slug}/posts`, {
        method: "POST",
        body: JSON.stringify({ title, body }),
      });
      setTitle("");
      setBody("");
      router.push(`/p/${post.id}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="container">
      <Nav />
      <header style={{ marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: "1rem", flexWrap: "wrap" }}>
          <h1 style={{ margin: 0 }}>{hub?.name ?? slug}</h1>
          {isOperator && (
            <button
              type="button"
              className="btn"
              style={{ background: "#8b0000", fontSize: "0.85rem" }}
              onClick={deleteSubpop}
            >
              Delete subpop (operator)
            </button>
          )}
        </div>
        <p className="meta" style={{ margin: "0.35rem 0 0" }}>
          {subpopLabel(slug)}
        </p>
        {hub?.description ? (
          <p style={{ margin: "0.75rem 0 0", color: "#444", lineHeight: 1.5, maxWidth: "42rem" }}>
            {hub.description}
          </p>
        ) : null}
      </header>

      {authed && <VerifyBanner verified={verified} />}

      {authed && verified ? (
        <form className="card" onSubmit={submitPost}>
          <h3 style={{ marginTop: 0 }}>New fractalpop</h3>
          <input
            className="input"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <textarea
            className="textarea"
            style={{ marginTop: "0.5rem" }}
            placeholder="Body (optional)"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
          <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
            Publish fractalpop
          </button>
        </form>
      ) : !authed ? (
        <AuthWall
          title="Sign up to post in this subpop"
          message="Browsing is open. Create an account to start a thread here."
        />
      ) : null}

      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      <h2 style={{ fontSize: "1.1rem", marginTop: "1.25rem" }}>Fractalpops</h2>

      {posts.length === 0 && (
        <p className="meta">No fractalpops yet.</p>
      )}

      {posts.map((post) => (
        <Link key={post.id} href={`/p/${post.id}`} className="card" style={{ display: "block" }}>
          <strong>{post.title}</strong>
          <div className="meta">
            @{post.author_handle} · {post.comment_count} replies · {new Date(post.created_at).toLocaleString()}
          </div>
        </Link>
      ))}
    </main>
  );
}
