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

  const filters: Filter[] = ["all", "proposed", "suggested", "active", "decayed"];

  return (
    <div className="dashboard">
      {/* Top nav / header */}
      <header className="dashboard-header">
        <div>
          <h1>Candidate Review Gate</h1>
          <div className="subtitle">AI-suggested lessons • Human promotion gate</div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <span className={`badge ${isLive ? "badge-live" : "badge-mock"}`}>
            {isLive ? "● LIVE API" : "○ MOCK MODE"}
          </span>
          <button onClick={() => refresh()} className="btn btn-ghost" style={{ padding: "0.5rem 1rem" }}>
            Refresh
          </button>
        </div>
      </header>

      {/* Toast messages */}
      {message && (
        <div role="alert" className="toast" onClick={() => setMessage(null)}>
          {message}
        </div>
      )}

      {/* Low confidence warning */}
      {showLowConfWarning && (
        <div role="alert" aria-live="assertive" className="warning">
          ⚠️ Low confidence warning — this candidate scored below 50%.
        </div>
      )}

      {/* Command bar with filters */}
      <div className="command-bar">
        <div className="filter-group" role="tablist" aria-label="Filter candidates">
          {filters.map((f) => (
            <button
              key={f}
              role="tab"
              aria-selected={filter === f}
              className={`filter-btn ${filter === f ? "active" : ""}`}
              onClick={() => {
                setFilter(f);
                refresh(f === "all" ? undefined : f);
              }}
            >
              {f}
            </button>
          ))}
        </div>

        <div style={{ marginLeft: "auto", color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
          {filtered.length} candidate{filtered.length !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Main content area */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: "1.5rem", padding: "0 2rem 3rem", alignItems: "start" }} className="detail-grid">
        {/* Candidates table */}
        <div>
          {filtered.length > 0 ? (
            <div className="table-container">
              <table role="grid" aria-label="Candidates">
                <thead>
                  <tr>
                    <th style={{ width: "38%" }}>Title</th>
                    <th style={{ width: "14%" }}>State</th>
                    <th style={{ width: "12%" }}>Confidence</th>
                    <th style={{ width: "18%" }}>Provenance</th>
                    <th style={{ width: "18%", textAlign: "right" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((c) => (
                    <tr
                      key={c.id}
                      onClick={() => onSelect(c.id)}
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          onSelect(c.id);
                        }
                      }}
                      style={{ background: selectedId === c.id ? "rgba(99,102,241,0.08)" : undefined }}
                    >
                      <td>{c.title}</td>
                      <td>
                        <span className={`state-badge state-${c.state}`}>{c.state}</span>
                      </td>
                      <td className="confidence">{(c.confidence * 100).toFixed(0)}%</td>
                      <td style={{ color: "var(--muted-foreground)", fontSize: "0.8125rem" }}>{c.provenance}</td>
                      <td style={{ textAlign: "right" }} onClick={(e) => e.stopPropagation()}>
                        <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
                          <button
                            onClick={() => doPromote(c.id)}
                            className="btn btn-primary"
                            style={{ padding: "0.4rem 0.9rem", fontSize: "0.75rem" }}
                          >
                            Promote
                          </button>
                          <button
                            onClick={() => doReject(c.id)}
                            className="btn btn-destructive"
                            style={{ padding: "0.4rem 0.9rem", fontSize: "0.75rem" }}
                          >
                            Reject
                          </button>
                          {c.contradictions && c.contradictions.length > 0 && (
                            <button
                              onClick={() => doResolve(c.id, c.contradictions![0])}
                              className="btn btn-ghost"
                              style={{ padding: "0.4rem 0.75rem", fontSize: "0.75rem" }}
                            >
                              Resolve
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              No candidates match the current filter.
            </div>
          )}
        </div>

        {/* Detail panel */}
        <div>
          {selected ? (
            <div className="detail-card">
              <h3>{selected.title}</h3>
              <p style={{ whiteSpace: "pre-wrap", color: "var(--card-foreground)", lineHeight: 1.65, marginBottom: "1.25rem" }}>
                {selected.content}
              </p>

              <div className="detail-meta">
                <div><strong>State:</strong> {selected.state}</div>
                <div><strong>Confidence:</strong> {(selected.confidence * 100).toFixed(1)}%</div>
                <div><strong>Provenance:</strong> {selected.provenance}</div>
              </div>

              {selected.confidenceBreakdown && (
                <div style={{ marginTop: "1.25rem", fontSize: "0.875rem" }}>
                  <div style={{ fontWeight: 600, marginBottom: "0.5rem", color: "var(--muted-foreground)" }}>Confidence Breakdown</div>
                  <ul style={{ paddingLeft: "1.1rem", margin: 0, color: "var(--muted-foreground)" }}>
                    {Object.entries(selected.confidenceBreakdown).map(([k, v]) => (
                      <li key={k} style={{ marginBottom: "0.1rem" }}>
                        {k}: {typeof v === "number" ? (v * 100).toFixed(0) + "%" : v}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {selected.contradictions && selected.contradictions.length > 0 && (
                <div style={{ marginTop: "1.25rem", padding: "1rem", background: "rgba(251,191,36,0.08)", borderRadius: "0.75rem", border: "1px solid rgba(251,191,36,0.2)" }}>
                  <div style={{ fontWeight: 600, marginBottom: "0.375rem" }}>Contradictions</div>
                  <div style={{ fontSize: "0.875rem", color: "var(--muted-foreground)" }}>{selected.contradictions.join(", ")}</div>
                  <button onClick={() => doResolve(selected.id, selected.contradictions![0])} className="btn btn-ghost" style={{ marginTop: "0.75rem", fontSize: "0.8125rem", padding: "0.5rem 1rem" }}>
                    Resolve Contradiction
                  </button>
                </div>
              )}

              <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                <button onClick={() => doPromote(selected.id)} className="btn btn-primary">Promote</button>
                <button onClick={() => doReject(selected.id)} className="btn btn-destructive">Reject</button>
                <button onClick={() => setSelected(null)} className="btn btn-ghost">Close</button>
              </div>

              {selected.state === "active" && (
                <div style={{ marginTop: "1rem", fontSize: "0.8125rem", color: "#34d399" }}>
                  ✓ This lesson is active in the knowledge graph
                </div>
              )}
              {selected.state === "decayed" && (
                <div style={{ marginTop: "1rem", fontSize: "0.8125rem", color: "#fbbf24" }}>
                  Decayed — not promoted (helper text for cand_12 / cand_18)
                </div>
              )}
            </div>
          ) : (
            <div className="detail-card" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "220px", color: "var(--muted-foreground)", textAlign: "center" }}>
              Select a candidate from the table to inspect details, promote, reject, or resolve contradictions.
            </div>
          )}
        </div>
      </div>

      <footer style={{ padding: "2rem", textAlign: "center", fontSize: "0.75rem", color: "var(--muted-foreground)", borderTop: "1px solid var(--border)", marginTop: "2rem" }}>
        praxis-lite • Dashboard &amp; Human Gate • Contract v1 • {isLive ? "Connected to live API" : "Offline mock mode"}
      </footer>
    </div>
  );
}
