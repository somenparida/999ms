export interface TrackPosition {
  track_id: number;
  timestamp: number;
  frame_number?: number;
  bbox: [number, number, number, number];
  confidence: number;
}

export interface Track {
  track_id: number;
  class: string;
  timestamp: number;
  bbox: [number, number, number, number];
  confidence: number;
  positions?: TrackPosition[];
}

