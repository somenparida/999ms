export interface Event {
  event_id: string;
  track_id: number;
  event_type: string;
  start_time: number;
  end_time: number;
  confidence: number;
  severity: "low" | "medium" | "high";
  reason: string;
  evidence_url?: string;
  clip_url?: string;
}

