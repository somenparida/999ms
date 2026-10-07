export interface EvidenceRecord {
  evidence_id: string;
  event_id: string;
  video_id: string;
  timestamp: number;
  image_url: string;
  clip_url?: string;
  resolution?: string;
  file_size_bytes?: number;
  created_at?: string;
}
