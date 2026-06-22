import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  listCandidates,
  getCandidate,
  promote,
  reject,
  resolveContradiction,
} from "./apiClient";

const BASE = "http://test-api";

beforeEach(() => {
  vi.stubEnv("VITE_PRAXIS_API_BASE_URL", BASE);
  vi.stubEnv("VITE_PRAXIS_API_TOKEN", "");
  vi.stubEnv("VITE_PRAXIS_ORG_ID", "default");
  global.fetch = vi.fn();
  vi.clearAllMocks();
});

describe("apiClient contract v1", () => {
  it("listCandidates fetches /candidates and maps", async () => {
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ candidates: [{ id: "c1", title: "t", content: "c", state: "proposed", confidence: 0.8, provenance: "p", createdAt: "2026-01-01T00:00:00Z" }] }),
    });
    const res = await listCandidates();
    expect(fetch).toHaveBeenCalledWith(`${BASE}/candidates`, expect.anything());
    expect(res[0].id).toBe("c1");
  });

  it("getCandidate returns null on 404", async () => {
    (fetch as any).mockResolvedValue({ ok: false, status: 404, statusText: "Not Found" });
    const res = await getCandidate("missing");
    expect(res).toBeNull();
  });

  it("getCandidate throws on non-404 error", async () => {
    (fetch as any).mockResolvedValue({ ok: false, status: 500, statusText: "Server Error" });
    await expect(getCandidate("boom")).rejects.toThrow("500 Server Error");
  });

  it("promote sends targetState and returns mapped candidate", async () => {
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: "c1", title: "t", content: "c", state: "suggested", confidence: 0.8, provenance: "p", createdAt: "2026-01-01T00:00:00Z" }),
    });
    const res = await promote("c1", "suggested");
    expect(fetch).toHaveBeenCalledWith(`${BASE}/candidates/c1/promote`, expect.objectContaining({ method: "POST" }));
    expect(res.state).toBe("suggested");
  });

  it("reject posts reason and returns candidate", async () => {
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: "c1", title: "t", content: "c", state: "decayed", confidence: 0.8, provenance: "p", createdAt: "2026-01-01T00:00:00Z" }),
    });
    const res = await reject("c1", "test reason");
    expect(res.state).toBe("decayed");
  });

  it("resolveContradiction posts to /contradictions/{id}/resolve", async () => {
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: "cand_9", title: "t", content: "c", state: "suggested", confidence: 0.8, provenance: "p", createdAt: "2026-01-01T00:00:00Z" }),
    });
    const res = await resolveContradiction("cand_9", "cand_16", "keep_a", "cand_9");
    expect(fetch).toHaveBeenCalledWith(`${BASE}/contradictions/cand_9__cand_16/resolve`, expect.anything());
    expect(res.id).toBe("cand_9");
  });
});
