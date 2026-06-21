import type { Candidate, PromotionState } from "./candidateModel";
import { candidateFromMapping } from "./candidateModel";

let store: Candidate[] = [];

export async function loadMockData(): Promise<void> {
  const res = await fetch("/mock-candidates.json");
  const raw = (await res.json()) as Record<string, unknown>[];
  store = raw.map(candidateFromMapping);
}

export function listCandidates(state?: PromotionState): Candidate[] {
  if (!state) return [...store];
  return store.filter((c) => c.state === state);
}

export function getCandidate(id: string): Candidate | undefined {
  return store.find((c) => c.id === id);
}

export function promote(id: string, targetState?: PromotionState): Candidate {
  const idx = store.findIndex((c) => c.id === id);
  if (idx === -1) throw new Error("not found");
  const cand = store[idx];
  const next = targetState ?? nextPromotionState(cand.state as PromotionState);
  if (!next) throw new Error("terminal");
  const updated: Candidate = {
    ...cand,
    state: next,
    auditTrail: [
      ...(cand.auditTrail ?? []),
      {
        action: "promote",
        timestamp: new Date().toISOString(),
        provenance: "react-mock",
        actor: "human",
        note: `to ${next}`,
      },
    ],
  };
  store[idx] = updated;
  return updated;
}

export function reject(id: string, reason?: string): Candidate {
  const idx = store.findIndex((c) => c.id === id);
  if (idx === -1) throw new Error("not found");
  const updated: Candidate = {
    ...store[idx],
    state: "decayed",
    auditTrail: [
      ...(store[idx].auditTrail ?? []),
      {
        action: "reject",
        timestamp: new Date().toISOString(),
        provenance: "react-mock",
        actor: "human",
        note: reason,
      },
    ],
  };
  store[idx] = updated;
  return updated;
}

export function resolveContradiction(
  primaryId: string,
  rivalId: string,
  resolution: "keep_a" | "keep_b",
  keepId: string
): Candidate {
  const keptIdx = store.findIndex((c) => c.id === keepId);
  if (keptIdx === -1) throw new Error("keep target not found");
  const loserId = keepId === primaryId ? rivalId : primaryId;
  const loserIdx = store.findIndex((c) => c.id === loserId);
  if (loserIdx !== -1) {
    store[loserIdx] = {
      ...store[loserIdx],
      state: "decayed",
      auditTrail: [
        ...(store[loserIdx].auditTrail ?? []),
        {
          action: "resolve_contradiction_loser",
          timestamp: new Date().toISOString(),
          provenance: "react-mock",
          actor: "human",
          note: `lost to ${keepId}`,
        },
      ],
    };
  }
  const kept = store[keptIdx];
  store[keptIdx] = {
    ...kept,
    auditTrail: [
      ...(kept.auditTrail ?? []),
      {
        action: "resolve_contradiction",
        timestamp: new Date().toISOString(),
        provenance: "react-mock",
        actor: "human",
        note: `${resolution} kept ${keepId}`,
      },
    ],
  };
  return store[keptIdx];
}

function nextPromotionState(state: PromotionState): PromotionState | undefined {
  if (state === "proposed") return "suggested";
  if (state === "suggested") return "active";
  return undefined;
}
