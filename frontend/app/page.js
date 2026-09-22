import Link from "next/link";
import Nav from "../components/Nav";

export default function Home() {
  return (
    <main className="container">
      <Nav />
      <section className="card">
        <h1 style={{ marginTop: 0 }}>Recast before you publish</h1>
        <p style={{ color: "#444", lineHeight: 1.5 }}>
          ProPopuli feels like the forum you already know — subpops (<strong>s\name</strong>), posts, threads — but
          replies must pass the Reframing Gate. Attack ideas, not people. Say the objection as an improvement or a
          condition.
        </p>
        <div className="home-actions">
          <Link href="/register" className="btn">
            Create account
          </Link>
          <Link href="/hubs" className="btn btn-secondary">
            Browse subpops
          </Link>
        </div>
        {process.env.NODE_ENV === "development" && (
          <p className="meta" style={{ marginTop: "1rem", marginBottom: 0 }}>
            Local dev:{" "}
            <a href="http://localhost:3000" rel="noopener noreferrer">
              http://localhost:3000
            </a>
          </p>
        )}
      </section>
    </main>
  );
}
