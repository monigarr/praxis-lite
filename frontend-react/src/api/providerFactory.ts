import * as mock from "./mockProvider";
import * as live from "./apiClient";
import type { Candidate, PromotionState } from "./candidateModel";

function useLive(): boolean {
  return Boolean(import.meta.env.VITE_PRAXIS_API_BASE_URL);
}

export async function initProvider(): Promise<void> {
  if (!useLive()) await mock.loadMockData();
}

export async function listCandidates(state?: PromotionState): Promise<Candidate[]> {
  return useLive() ? live.listCandidates(state) : mock.listCandidates(state);
}

export async function getCandidate(id: string): Promise<Candidate | null> {
  return useLive() ? live.getCandidate(id) : mock.getCandidate(id) ?? null;
}

export async function promote(id: string, target?: PromotionState): Promise<Candidate> {
  return useLive() ? live.promote(id, target) : mock.promote(id, target);
}

export async function reject(id: string, reason?: string): Promise<Candidate> {
  return useLive() ? live.reject(id, reason) : mock.reject(id, reason);
}

export async function resolveContradiction(
  primary: string,
  rival: string,
  resolution: "keep_a" | "keep_b",
  keep: string
): Promise<Candidate> {
  return useLive()
    ? live.resolveContradiction(primary, rival, resolution, keep)
    : mock.resolveContradiction(primary, rival, resolution, keep);
}
