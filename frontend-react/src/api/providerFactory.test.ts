import { describe, it, expect, vi, beforeEach } from "vitest";
import * as providerFactory from "./providerFactory";

// Note: providerFactory uses import.meta.env at module load; tests verify delegation shape
describe("providerFactory", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_PRAXIS_API_BASE_URL", "");
  });

  it("exports the expected async functions", () => {
    expect(typeof providerFactory.initProvider).toBe("function");
    expect(typeof providerFactory.listCandidates).toBe("function");
    expect(typeof providerFactory.promote).toBe("function");
    expect(typeof providerFactory.reject).toBe("function");
    expect(typeof providerFactory.resolveContradiction).toBe("function");
  });
});
