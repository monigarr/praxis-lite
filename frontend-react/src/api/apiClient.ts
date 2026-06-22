import type { Candidate, PromotionState } from "./candidateModel";
import { candidateFromMapping } from "./candidateModel";

function getBase(): string {
  return import.meta.env.VITE_PRAXIS_API_BASE_URL ?? "";
}
function getToken(): string {
  return import.meta.env.VITE_PRAXIS_API_TOKEN ?? "";
}
function getOrg(): string {
  return import.meta.env.VITE_PRAXIS_ORG_ID ?? "default";
}

function headers() {
  const h: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
    "X-Praxis-Contract": "1",
    "X-Praxis-Org": getOrg(),
  };
  const token = getToken();
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${getBase()}${path}`, { ...init, headers: { ...headers(), ...init?.headers } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export async function listCandidates(state?: PromotionState): Promise<Candidate[]> {
  const qs = state ? `?state=${state}` : "";
  const data = await request<Record<string, unknown>[]>(`/candidates${qs}`);
  const arr = Array.isArray(data) ? data : (data as any).candidates ?? [];
  return arr.map(candidateFromMapping);
}

export async function getCandidate(id: string): Promise<Candidate | null> {
  try {
    const data = await request<Record<string, unknown>>(`/candidates/${id}`);
    return candidateFromMapping(data);
  } catch (e) {
    if (String(e).includes("404")) return null;
    throw e;
  }
}

export async function promote(id: string, targetState?: PromotionState): Promise<Candidate> {
  const body = targetState ? { targetState } : {};
  const data = await request<Record<string, unknown>>(`/candidates/${id}/promote`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  return candidateFromMapping(data);
}

export async function reject(id: string, reason?: string): Promise<Candidate> {
  const body = reason ? { reason } : {};
  const data = await request<Record<string, unknown>>(`/candidates/${id}/reject`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  return candidateFromMapping(data);
}

export async function resolveContradiction(
  primaryId: string,
  rivalId: string,
  resolution: "keep_a" | "keep_b",
  keepId: string
): Promise<Candidate> {
  const body = { resolution, keepId };
  const data = await request<Record<string, unknown>>(`/contradictions/${primaryId}__${rivalId}/resolve`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  return candidateFromMapping(data);
}
