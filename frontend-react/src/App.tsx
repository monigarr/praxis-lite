import { useEffect, useMemo, useState } from "react";
import type { Candidate, PromotionState } from "./api/candidateModel";
import {
  initProvider,
  listCandidates,
  getCandidate,
  promote,
  reject,
  resolveContradiction,
} from "./api/providerFactory";

type Filter = "all" | PromotionState;

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [showLowConfWarning, setShowLowConfWarning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    const env = import.meta.env.VITE_PRAXIS_API_BASE_URL;
    setIsLive(Boolean(env));
    initProvider().then(() => refresh());
  }, []);

  async function refresh(state?: PromotionState) {
    const data = await listCandidates(state);
    setCandidates(data);
  }

  const filtered = useMemo(() => {
    if (filter === "all") return candidates;
    return candidates.filter((c) => c.state === filter);
  }, [candidates, filter]);

  async function onSelect(id: string) {
    setSelectedId(id);
    const cand = await getCandidate(id);
    setSelected(cand);
    if (cand && cand.confidence < 0.5) {
      setShowLowConfWarning(true);
      setTimeout(() => setShowLowConfWarning(false), 4000);
    }
  }

  async function doPromote(id: string) {
    const cand = candidates.find((c) => c.id === id);
    if (!cand) return;
    const next = cand.state === "proposed" ? "suggested" : "active";
    if (cand.confidence < 0.5) {
      if (!confirm("Low confidence (<50%). Promote anyway?")) return;
    }
    const updated = await promote(id, next);
    setMessage(`Promoted ${id} → ${next}`);
    setSelected(updated);
    await refresh();
  }

  async function doReject(id: string) {
    const reason = prompt("Reason for rejection (optional)?") || undefined;
    const updated = await reject(id, reason);
    setMessage(`Rejected ${id}`);
    setSelected(updated);
    await refresh();
  }

  async function doResolve(primary: string, rival: string) {
    const keep = confirm(`Keep ${primary} (left) or ${rival} (right)?\nOK = keep left`) ? primary : rival;
    const res = keep === primary ? "keep_a" : "keep_b";
    const updated = await resolveContradiction(primary, rival, res, keep);
    setMessage(`Resolved contradiction: kept ${keep}`);
    setSelected(updated);
    await refresh();
  }

  return (
    <div style={{ fontFamily: "system-ui", padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>PRAXIS Human Gate Dashboard</h1>
        <div>
          <span style={{ background: isLive ? "#d1fae5" : "#fef3c7", padding: "2px 8px", borderRadius: 4 }}>
            {isLive ? "LIVE API" : "MOCK MODE"}
          </span>
          <button onClick={() => refresh()} style={{ marginLeft: 12 }}>Refresh</button>
        </div>
      </header>

      {message && <div role="alert" style={{ background: "#ecfdf5", padding: 8, margin: "12px 0" }}>{message}</div>}

      {showLowConfWarning && (
        <div role="alert" aria-live="assertive" style={{ background: "#fef2f2", color: "#b91c1c", padding: 8, marginBottom: 12 }}>
          ⚠️ Low confidence warning — this candidate scored below 50%.
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        {(["all", "proposed", "suggested", "active", "decayed"] as const).map((f) => (
          <button
            key={f}
            onClick={() => {
              setFilter(f);
              refresh(f === "all" ? undefined : f);
            }}
            style={{ marginRight: 8, fontWeight: filter === f ? "bold" : "normal" }}
          >
            {f}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: 24 }}>
        {/* List */}
        <div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "2px solid #e5e7eb" }}>
                <th>Title</th>
                <th>State</th>
                <th>Confidence</th>
                <th>Provenance</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => onSelect(c.id)}
                  style={{ cursor: "pointer", background: selectedId === c.id ? "#f3f4f6" : "white" }}
                >
                  <td>{c.title}</td>
                  <td>{c.state}</td>
                  <td>{(c.confidence * 100).toFixed(0)}%</td>
                  <td style={{ fontSize: 12, color: "#6b7280" }}>{c.provenance}</td>
                  <td>
                    <button onClick={(e) => { e.stopPropagation(); doPromote(c.id); }}>Promote</button>
                    <button onClick={(e) => { e.stopPropagation(); doReject(c.id); }}>Reject</button>
                    {c.contradictions && c.contradictions.length > 0 && (
                      <button onClick={(e) => { e.stopPropagation(); doResolve(c.id, c.contradictions![0]); }}>
                        Resolve
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Detail panel */}
        <div>
          {selected ? (
            <div style={{ border: "1px solid #e5e7eb", padding: 16, borderRadius: 8 }}>
              <h3>{selected.title}</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{selected.content}</p>
              <div style={{ fontSize: 13, color: "#6b7280" }}>
                <div>State: {selected.state}</div>
                <div>Confidence: {(selected.confidence * 100).toFixed(1)}%</div>
                <div>Provenance: {selected.provenance}</div>
              </div>

              {selected.confidenceBreakdown && (
                <div style={{ marginTop: 12 }}>
                  <strong>Confidence Breakdown</strong>
                  <ul style={{ fontSize: 13 }}>
                    {Object.entries(selected.confidenceBreakdown).map(([k, v]) => (
                      <li key={k}>{k}: {typeof v === "number" ? (v * 100).toFixed(0) + "%" : v}</li>
                    ))}
                  </ul>
                </div>
              )}

              {selected.contradictions && selected.contradictions.length > 0 && (
                <div style={{ marginTop: 12, padding: 8, background: "#fefce8" }}>
                  <strong>Contradictions</strong>
                  <div>{selected.contradictions.join(", ")}</div>
                  <button onClick={() => doResolve(selected.id, selected.contradictions![0])}>
                    Resolve Contradiction
                  </button>
                </div>
              )}

              <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                <button onClick={() => doPromote(selected.id)}>Promote</button>
                <button onClick={() => doReject(selected.id)}>Reject</button>
                <button onClick={() => setSelected(null)}>Close</button>
              </div>

              {selected.state === "active" && (
                <div style={{ marginTop: 8, fontSize: 12, color: "#166534" }}>
                  ✓ This lesson is active in the knowledge graph
                </div>
              )}
              {selected.state === "decayed" && (
                <div style={{ marginTop: 8, fontSize: 12, color: "#854d0e" }}>
                  Decayed — not promoted (helper text for cand_12 / cand_18)
                </div>
              )}
            </div>
          ) : (
            <div style={{ color: "#6b7280" }}>Select a candidate from the table to inspect details, promote, reject, or resolve contradictions.</div>
          )}
        </div>
      </div>

      <footer style={{ marginTop: 48, fontSize: 12, color: "#9ca3af" }}>
        Monica Peters — Dashboard &amp; Human Gate pillar • Contract v1 • {isLive ? "Connected to live API" : "Offline mock mode"}
      </footer>
    </div>
  );
}
