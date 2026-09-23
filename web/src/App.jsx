import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [line, setLine] = useState([]);
  const [explorer, setExplorer] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;
    const params = new URLSearchParams();
    if (line.length > 0) params.set("line", line.join(","));

    fetch(`${API_BASE}/api/explorer?${params}`)
      .then(async (response) => {
        if (!response.ok) {
          const body = await response.json();
          throw new Error(body.detail ?? "Request failed");
        }
        return response.json();
      })
      .then((data) => {
        if (ignore) return;
        setExplorer(data);
        setError(null);
      })
      .catch((err) => {
        if (ignore) return;
        setError(err.message);
      });

    return () => {
      ignore = true;
    };
  }, [line]);

  if (error) return <p>Error: {error}</p>;
  if (!explorer) return <p>Loading…</p>;

  return (
    <main>
      <h1>Chess Opening Explorer</h1>
      <p>Line: {line.length > 0 ? line.join(" ") : "(start)"}</p>
      <p>
        {explorer.total_games} games · {(explorer.reach_share * 100).toFixed(1)}% reach share
      </p>
      {explorer.continuations.length === 0 && <p>No games behind this position.</p>}
      <ul>
        {explorer.continuations.map((continuation) => (
          <li key={continuation.move}>
            <button onClick={() => setLine([...line, continuation.move])}>
              {continuation.move} — {continuation.games} games (
              {(continuation.share * 100).toFixed(1)}%)
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
