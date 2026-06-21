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
type View = "dashboard" | "candidates" | "graph" | "evals" | "api";

export default function App() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<Candidate | null>(null);
  const [showLowConfWarning, setShowLowConfWarning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [currentView, setCurrentView] = useState<View>("dashboard");

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

  const navItems: { view: View; label: string; icon: React.ReactNode; title: string }[] = [
    {
      view: "dashboard",
      label: "Dashboard",
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>,
      title: "Human Gate Dashboard — review, promote, reject candidates",
    },
    {
      view: "candidates",
      label: "Candidates",
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>,
      title: "All Candidates — table and quick actions",
    },
    {
      view: "graph",
      label: "Graph",
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
      title: "Knowledge Graph — active & promoted lessons",
    },
    {
      view: "evals",
      label: "Evals",
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>,
      title: "Evaluations & Metrics — deterministic checks",
    },
    {
      view: "api",
      label: "API",
      icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
      title: "API Contracts & Integration",
    },
  ];

  return (
    <div className="dashboard">
      {/* Top nav / header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1 className="header-title">Candidate Review Gate</h1>
            <div className="subtitle">AI-suggested lessons • Human promotion gate</div>
          </div>

          {/* Polished navigation icons for all in-app sections */}
          <nav className="app-nav" aria-label="Main navigation">
            {navItems.map((item) => (
              <button
                key={item.view}
                className={`app-nav-item ${currentView === item.view ? "active" : ""}`}
                onClick={() => setCurrentView(item.view)}
                title={item.title}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="header-actions">
          <span className={`badge ${isLive ? "badge-live" : "badge-mock"}`}>
            {isLive ? "● LIVE API" : "○ MOCK MODE"}
          </span>
          <button onClick={() => refresh()} className="btn btn-ghost header-refresh">
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

      {/* ===================================================== */}
      {/* DASHBOARD VIEW — full original functionality preserved */}
      {/* ===================================================== */}
      {currentView === "dashboard" && (
        <>
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

            <div className="candidate-count">
              {filtered.length} candidate{filtered.length !== 1 ? "s" : ""}
            </div>
          </div>

          {/* Main content area */}
          <div className="main-grid detail-grid">
            {/* Candidates table */}
            <div>
              {filtered.length > 0 ? (
                <div className="table-container">
                  <table role="grid" aria-label="Candidates">
                    <thead>
                      <tr>
                        <th className="col-title">Title</th>
                        <th className="col-state">State</th>
                        <th className="col-confidence">Confidence</th>
                        <th className="col-provenance">Provenance</th>
                        <th className="col-actions">Actions</th>
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
                          className={selectedId === c.id ? "row-selected" : undefined}
                        >
                          <td>{c.title}</td>
                          <td>
                            <span className={`state-badge state-${c.state}`}>{c.state}</span>
                          </td>
                          <td className="confidence">{(c.confidence * 100).toFixed(0)}%</td>
                          <td className="provenance-cell">{c.provenance}</td>
                          <td className="actions-cell" onClick={(e) => e.stopPropagation()}>
                            <div className="action-buttons">
                              <button
                                onClick={() => doPromote(c.id)}
                                className="btn btn-primary action-btn-sm"
                              >
                                Promote
                              </button>
                              <button
                                onClick={() => doReject(c.id)}
                                className="btn btn-destructive action-btn-sm"
                              >
                                Reject
                              </button>
                              {c.contradictions && c.contradictions.length > 0 && (
                                <button
                                  onClick={() => doResolve(c.id, c.contradictions![0])}
                                  className="btn btn-ghost action-btn-resolve"
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
                  <p className="content-paragraph">{selected.content}</p>

                  <div className="detail-meta">
                    <div><strong>State:</strong> {selected.state}</div>
                    <div><strong>Confidence:</strong> {(selected.confidence * 100).toFixed(1)}%</div>
                    <div><strong>Provenance:</strong> {selected.provenance}</div>
                  </div>

                  {selected.confidenceBreakdown && (
                    <div className="breakdown-container">
                      <div className="breakdown-header">Confidence Breakdown</div>
                      <ul className="breakdown-list">
                        {Object.entries(selected.confidenceBreakdown).map(([k, v]) => (
                          <li key={k} className="breakdown-item">
                            {k}: {typeof v === "number" ? (v * 100).toFixed(0) + "%" : v}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {selected.contradictions && selected.contradictions.length > 0 && (
                    <div className="contradiction-box">
                      <div className="contradiction-title">Contradictions</div>
                      <div className="contradiction-text">{selected.contradictions.join(", ")}</div>
                      <button onClick={() => doResolve(selected.id, selected.contradictions![0])} className="btn btn-ghost resolve-btn">
                        Resolve Contradiction
                      </button>
                    </div>
                  )}

                  <div className="detail-actions">
                    <button onClick={() => doPromote(selected.id)} className="btn btn-primary">Promote</button>
                    <button onClick={() => doReject(selected.id)} className="btn btn-destructive">Reject</button>
                    <button onClick={() => setSelected(null)} className="btn btn-ghost">Close</button>
                  </div>

                  {selected.state === "active" && (
                    <div className="status-active">
                      ✓ This lesson is active in the knowledge graph
                    </div>
                  )}
                  {selected.state === "decayed" && (
                    <div className="status-decayed">
                      Decayed — not promoted (helper text for cand_12 / cand_18)
                    </div>
                  )}
                </div>
              ) : (
                <div className="detail-card empty-detail">
                  Select a candidate from the table to inspect details, promote, reject, or resolve contradictions.
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* ===================================================== */}
      {/* CANDIDATES VIEW — clean list alternative             */}
      {/* ===================================================== */}
      {currentView === "candidates" && (
        <div className="section-container">
          <div className="section-header">
            <h2>All Candidates</h2>
            <p className="section-subtitle">Quick overview of every candidate in the system</p>
          </div>
          <div className="table-container">
            <table role="grid" aria-label="All Candidates">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>State</th>
                  <th>Confidence</th>
                  <th>Provenance</th>
                </tr>
              </thead>
              <tbody>
                {candidates.length > 0 ? (
                  candidates.map((c) => (
                    <tr key={c.id} onClick={() => { setCurrentView("dashboard"); onSelect(c.id); }} style={{ cursor: "pointer" }}>
                      <td>{c.title}</td>
                      <td><span className={`state-badge state-${c.state}`}>{c.state}</span></td>
                      <td className="confidence">{(c.confidence * 100).toFixed(0)}%</td>
                      <td className="provenance-cell">{c.provenance}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan={4} className="empty-state">No candidates loaded yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div style={{ marginTop: "1rem", color: "var(--muted-foreground)", fontSize: "0.875rem" }}>
            Click any row to open it in the Dashboard for full actions.
          </div>
        </div>
      )}

      {/* ===================================================== */}
      {/* GRAPH VIEW — Knowledge Graph summary                 */}
      {/* ===================================================== */}
      {currentView === "graph" && (
        <div className="section-container">
          <div className="section-header">
            <h2>Knowledge Graph</h2>
            <p className="section-subtitle">Active and promoted lessons currently in the graph</p>
          </div>

          <div className="detail-card" style={{ marginBottom: "1.5rem" }}>
            <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
              <div>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--success)" }}>
                  {candidates.filter(c => c.state === "active").length}
                </div>
                <div style={{ color: "var(--muted-foreground)" }}>Active Lessons</div>
              </div>
              <div>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--accent)" }}>
                  {candidates.filter(c => c.state === "suggested").length}
                </div>
                <div style={{ color: "var(--muted-foreground)" }}>Suggested</div>
              </div>
              <div>
                <div style={{ fontSize: "2rem", fontWeight: 700, color: "var(--warning)" }}>
                  {candidates.filter(c => c.state === "proposed").length}
                </div>
                <div style={{ color: "var(--muted-foreground)" }}>Proposed</div>
              </div>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Lesson</th>
                  <th>State</th>
                  <th>Provenance</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {candidates.filter(c => ["active", "suggested"].includes(c.state)).length > 0 ? (
                  candidates
                    .filter(c => ["active", "suggested"].includes(c.state))
                    .map(c => (
                      <tr key={c.id}>
                        <td>{c.title}</td>
                        <td><span className={`state-badge state-${c.state}`}>{c.state}</span></td>
                        <td className="provenance-cell">{c.provenance}</td>
                        <td className="confidence">{(c.confidence * 100).toFixed(0)}%</td>
                      </tr>
                    ))
                ) : (
                  <tr><td colSpan={4} className="empty-state">No promoted lessons yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ===================================================== */}
      {/* EVALS VIEW — Evaluations & Metrics                   */}
      {/* ===================================================== */}
      {currentView === "evals" && (
        <div className="section-container">
          <div className="section-header">
            <h2>Evaluations & Metrics</h2>
            <p className="section-subtitle">Deterministic checks and quality signals</p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1.5rem" }}>
            <div className="detail-card">
              <div style={{ fontSize: "0.875rem", color: "var(--muted-foreground)" }}>Total Candidates</div>
              <div style={{ fontSize: "2.25rem", fontWeight: 700 }}>{candidates.length}</div>
            </div>
            <div className="detail-card">
              <div style={{ fontSize: "0.875rem", color: "var(--muted-foreground)" }}>Low Confidence (&lt;50%)</div>
              <div style={{ fontSize: "2.25rem", fontWeight: 700, color: "#fda4af" }}>
                {candidates.filter(c => c.confidence < 0.5).length}
              </div>
            </div>
            <div className="detail-card">
              <div style={{ fontSize: "0.875rem", color: "var(--muted-foreground)" }}>Active in Graph</div>
              <div style={{ fontSize: "2.25rem", fontWeight: 700, color: "var(--success)" }}>
                {candidates.filter(c => c.state === "active").length}
              </div>
            </div>
          </div>

          <div className="detail-card" style={{ marginTop: "1.5rem" }}>
            <div style={{ fontWeight: 600, marginBottom: "0.75rem" }}>How evaluations work</div>
            <div style={{ color: "var(--muted-foreground)", lineHeight: 1.6 }}>
              The knowledge pipeline runs deterministic checks on every candidate before it reaches the Human Gate.
              Low-confidence items are flagged here and in the dashboard. See <code>knowledge/evals/</code> for the full harness.
            </div>
          </div>
        </div>
      )}

      {/* ===================================================== */}
      {/* API VIEW — Contracts & Integration                   */}
      {/* ===================================================== */}
      {currentView === "api" && (
        <div className="section-container">
          <div className="section-header">
            <h2>API & Contracts</h2>
            <p className="section-subtitle">Live integration status and contract references</p>
          </div>

          <div className="detail-card">
            <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
              <span className={`badge ${isLive ? "badge-live" : "badge-mock"}`}>
                {isLive ? "● CONNECTED TO LIVE API" : "○ RUNNING IN MOCK MODE"}
              </span>
            </div>

            <div style={{ color: "var(--muted-foreground)", lineHeight: 1.7 }}>
              <p><strong>Base URL:</strong> {import.meta.env.VITE_PRAXIS_API_BASE_URL || "Not configured (mock mode)"}</p>
              <p style={{ marginTop: "1rem" }}>
                Full contract documentation lives in <code>docs/integration/candidate-api-v1.md</code>.
                The React client uses the same contract as the Python frontend layer.
              </p>
            </div>

            <div style={{ marginTop: "2rem" }}>
              <button onClick={() => setCurrentView("dashboard")} className="btn btn-primary">
                Return to Dashboard
              </button>
            </div>
          </div>
        </div>
      )}

      <footer className="app-footer">
        praxis-lite • Dashboard &amp; Human Gate • Contract v1 • {isLive ? "Connected to live API" : "Offline mock mode"}
      </footer>
    </div>
  );
}
