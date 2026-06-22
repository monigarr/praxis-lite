import { describe, it, expect } from "vitest";
import { candidateFromMapping, type Candidate } from "./candidateModel";

describe("candidateFromMapping", () => {
  it("maps camelCase and snake_case aliases", () => {
    const raw = {
      id: "c1",
      title: "t",
      content: "c",
      state: "proposed",
      confidence: 0.8,
      provenance: "p",
      created_at: "2026-01-01",
      confidence_breakdown: { frequency: 1 },
      audit_trail: [{ action: "x" }],
    };
    const c: Candidate = candidateFromMapping(raw);
    expect(c.createdAt).toBe("2026-01-01");
    expect(c.confidenceBreakdown).toEqual({ frequency: 1 });
    expect(c.auditTrail).toEqual([{ action: "x" }]);
  });

  it("handles missing optional fields", () => {
    const raw = { id: "c2", title: "t", content: "c", state: "active", confidence: 0.5, provenance: "p" };
    const c = candidateFromMapping(raw);
    expect(c.createdAt).toBeDefined();
    expect(c.contradictions).toBeUndefined();
  });
});
