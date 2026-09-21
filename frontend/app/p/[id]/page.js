"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import AuthWall from "../../../components/AuthWall";
import Nav from "../../../components/Nav";
import VerifyBanner from "../../../components/VerifyBanner";
import { authHref } from "../../../lib/auth";
import { CONTENT_POLICY_MESSAGE, contentPolicyViolation } from "../../../lib/contentPolicy";
import { api, getToken } from "../../../lib/api";
import { subpopLabel, subpopPath } from "../../../lib/subpop";

function CommentTree({ comments, parentId = null, depth = 0 }) {
  const nodes = comments.filter((c) => c.parent_id === parentId);
  return nodes.map((c) => (
    <div key={c.id} className="comment" style={{ marginLeft: depth ? "1rem" : 0 }}>
      <div className="card">
        <div className="meta">
          @{c.author_handle} · {new Date(c.created_at).toLocaleString()}
        </div>
        <p style={{ whiteSpace: "pre-wrap", marginBottom: 0 }}>{c.body}</p>
      </div>
      <CommentTree comments={comments} parentId={c.id} depth={depth + 1} />
    </div>
  ));
}

export default function PostPage() {
  const { id } = useParams();
  const router = useRouter();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [body, setBody] = useState("");
  const [gate, setGate] = useState(null);
  const [error, setError] = useState("");
  const [authed, setAuthed] = useState(false);
  const [verified, setVerified] = useState(true);

  const load = async () => {
    const [p, c] = await Promise.all([api(`/posts/${id}`), api(`/posts/${id}/comments`)]);
    setPost(p);
    setComments(c);
  };

  useEffect(() => {
    const tok = getToken();
    setAuthed(!!tok);
    if (tok) {
      api("/me")
        .then((u) => setVerified(u.email_verified))
        .catch(() => setVerified(true));
    }
    if (id) {
      load().catch((e) => setError(e.message));
    }
  }, [id]);

  const replyCount = useMemo(() => comments.length, [comments]);

  async function submitReply(e) {
    e.preventDefault();
    if (!getToken()) {
      router.push(authHref("/register", `/p/${id}`));
      return;
    }
    setError("");
    setGate(null);
    if (contentPolicyViolation(body)) {
      setError(CONTENT_POLICY_MESSAGE);
      return;
    }
    try {
      await api(`/posts/${id}/comments`, {
        method: "POST",
        body: JSON.stringify({ body }),
      });
      setBody("");
      await load();
    } catch (err) {
      if (err.status === 422 && err.payload?.detail) {
        const d = err.payload.detail;
        setGate(typeof d === "object" ? d : { detail: String(d) });
      } else {
        setError(err.message);
      }
    }
  }

  if (!post && !error) return <main className="container">Loading…</main>;

  return (
    <main className="container">
      <Nav />
      {post && (
        <>
          <div className="meta">
            <Link href={subpopPath(post.hub_slug)}>{subpopLabel(post.hub_slug)}</Link>
          </div>
          <article className="card">
            <h1 style={{ marginTop: 0 }}>{post.title}</h1>
            {post.body && <p style={{ whiteSpace: "pre-wrap" }}>{post.body}</p>}
            <div className="meta">
              @{post.author_handle} · {replyCount} replies
            </div>
          </article>

          {authed && <VerifyBanner verified={verified} />}

          {authed && verified ? (
            <form className="card" onSubmit={submitReply}>
              <h3 style={{ marginTop: 0 }}>Reply (Gate enforced)</h3>
              <textarea
                className="textarea"
                placeholder="State the objection as an improvement or a condition…"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                required
              />
              {gate && (
                <div className="challenge">
                  <strong>Reframing Gate</strong>
                  <p style={{ margin: "0.5rem 0" }}>{gate.detail || gate.challenge}</p>
                  {gate.challenge && gate.detail && <p style={{ margin: 0 }}>{gate.challenge}</p>}
                  {gate.reasons?.length > 0 && (
                    <ul style={{ marginBottom: 0 }}>
                      {gate.reasons.map((r) => (
                        <li key={r}>{r}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
              <button className="btn" type="submit" style={{ marginTop: "0.75rem" }}>
                Publish reply
              </button>
            </form>
          ) : !authed ? (
            <AuthWall
              title="Sign up to reply"
              message="Read this thread freely. Replies require an account and must pass the Reframing Gate."
            />
          ) : null}

          <h3>Thread</h3>
          <CommentTree comments={comments} />
        </>
      )}
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
    </main>
  );
}
