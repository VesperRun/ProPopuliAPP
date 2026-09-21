import Link from "next/link";
import Nav from "../components/Nav";

export default function Home() {
  return (
    <main className="container">
      <Nav />
      <section className="card">
        <h1 style={{ marginTop: 0 }}>Recast before you publish</h1>
        <p style={{ color: "#444", lineHeight: 1.5 }}>
          ProPopuli patterns Reddit — hubs, posts, threads — but replies must pass the Reframing Gate.
          Attack ideas, not people. Say the objection as an improvement or a condition.
        </p>
        <Link href="/hubs" className="btn" style={{ display: "inline-block", marginTop: "0.5rem" }}>
          Browse hubs
        </Link>
      </section>
    </main>
  );
}
