export type PromotionState = "proposed" | "suggested" | "active" | "decayed";

export interface ConfidenceBreakdown {
  frequency: number;
  recency: number;
  breadth: number;
  frequencyRationale?: string;
  recencyRationale?: string;
  breadthRationale?: string;
}

export interface AuditEntry {
  action: string;
  timestamp: string;
  provenance: string;
  actor: string;
  note?: string;
}

export interface Candidate {
  id: string;
  title: string;
  content: string;
  state: PromotionState | string;
  confidence: number;
  provenance: string;
  createdAt: string;
  confidenceBreakdown?: ConfidenceBreakdown;
  contradictions?: string[];
  auditTrail?: AuditEntry[];
  // extra fields are allowed and ignored by the UI
  [key: string]: unknown;
}

export function candidateFromMapping(data: Record<string, unknown>): Candidate {
  return {
    id: String(data.id),
    title: String(data.title),
    content: String(data.content),
    state: String(data.state) as PromotionState,
    confidence: Number(data.confidence),
    provenance: String(data.provenance),
    createdAt: String(data.createdAt ?? data.created_at ?? new Date().toISOString()),
    confidenceBreakdown: (data.confidenceBreakdown ?? data.confidence_breakdown) as
      | ConfidenceBreakdown
      | undefined,
    contradictions: data.contradictions as string[] | undefined,
    auditTrail: (data.auditTrail ?? data.audit_trail) as AuditEntry[] | undefined,
  };
}
