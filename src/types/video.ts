export interface Video {
  video_id: string;
  title: string;
  filename: string;
  duration_seconds: number;
  fps: number;
  resolution: string;
  uploaded_at: string;
  url: string;
  thumbnail_url?: string;
  status: 'unprocessed' | 'processing' | 'completed' | 'failed';
}

export interface AnalysisStatus {
  video_id: string;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number; // 0 to 100
  current_step?: string;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

export interface TimelineEntry {
  timestamp: number;
  formatted_time: string;
  track_id: number;
  label: string;
  type: 'behaviour' | 'event';
  severity?: 'low' | 'medium' | 'high';
  description: string;
}

export interface SystemAnalytics {
  people_detected: number;
  active_tracks: number;
  normal_events: number;
  abnormal_events: number;
  high_risk_events: number;
  events_by_type: { name: string; count: number }[];
  events_by_severity: { severity: 'low' | 'medium' | 'high'; count: number }[];
  activity_over_time: { time: string; count: number; abnormal: number }[];
  behaviour_distribution: { behaviour: string; count: number }[];
}
