export default function GateChallenge({ gate }) {
  if (!gate) return null;
  return (
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
  );
}
