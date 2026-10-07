import { Track, Behaviour, Event, Video, AnalysisStatus, SystemAnalytics, TimelineEntry, Zone, EvidenceRecord } from '@/types';

export const MOCK_VIDEOS: Video[] = [
  {
    video_id: 'vid-autovision-001',
    title: 'Surveillance Feed - Sector 4 Industrial Gate',
    filename: 'sector4_industrial_gate_hd.mp4',
    duration_seconds: 151, // 02:31
    fps: 30,
    resolution: '1920x1080',
    uploaded_at: '2026-10-07T09:30:00Z',
    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    thumbnail_url: 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=400&q=80',
    status: 'completed',
  },
  {
    video_id: 'vid-autovision-002',
    title: 'Warehouse Logistics Loading Dock B',
    filename: 'warehouse_dock_b.mp4',
    duration_seconds: 180,
    fps: 25,
    resolution: '1920x1080',
    uploaded_at: '2026-10-07T10:15:00Z',
    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    thumbnail_url: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&q=80',
    status: 'completed',
  },
];

export const MOCK_TRACKS: Track[] = [
  { track_id: 1, class: 'person', timestamp: 12.5, bbox: [120, 200, 240, 520], confidence: 0.96 },
  { track_id: 1, class: 'person', timestamp: 20.0, bbox: [160, 210, 280, 530], confidence: 0.94 },
  { track_id: 1, class: 'person', timestamp: 35.0, bbox: [220, 220, 340, 540], confidence: 0.91 },
  { track_id: 3, class: 'person', timestamp: 40.0, bbox: [450, 180, 560, 490], confidence: 0.95 },
  { track_id: 3, class: 'person', timestamp: 74.0, bbox: [470, 185, 580, 495], confidence: 0.93 },
  { track_id: 3, class: 'person', timestamp: 98.0, bbox: [472, 185, 582, 495], confidence: 0.92 },
  { track_id: 7, class: 'person', timestamp: 13.0, bbox: [700, 220, 810, 530], confidence: 0.97 },
  { track_id: 7, class: 'person', timestamp: 31.0, bbox: [620, 240, 730, 550], confidence: 0.95 },
  { track_id: 7, class: 'person', timestamp: 42.0, bbox: [550, 260, 660, 570], confidence: 0.94 },
  { track_id: 7, class: 'person', timestamp: 55.0, bbox: [540, 270, 650, 580], confidence: 0.93 },
  { track_id: 7, class: 'person', timestamp: 62.0, bbox: [480, 280, 590, 590], confidence: 0.89 },
  { track_id: 9, class: 'person', timestamp: 100.0, bbox: [300, 250, 410, 560], confidence: 0.93 },
  { track_id: 9, class: 'person', timestamp: 111.0, bbox: [310, 320, 490, 580], confidence: 0.91 },
  { track_id: 9, class: 'person', timestamp: 126.0, bbox: [310, 380, 510, 580], confidence: 0.88 },
];

export const MOCK_BEHAVIOURS: Behaviour[] = [
  { track_id: 1, behaviour: 'Walking', start_time: 10, end_time: 25, confidence: 0.95 },
  { track_id: 1, behaviour: 'Loitering Near Perimeter', start_time: 25, end_time: 40, confidence: 0.82 },
  { track_id: 3, behaviour: 'Walking', start_time: 35, end_time: 73, confidence: 0.91 },
  { track_id: 3, behaviour: 'Prolonged Inactivity (Stationary)', start_time: 74, end_time: 105, confidence: 0.89 },
  { track_id: 7, behaviour: 'Walking', start_time: 13, end_time: 30, confidence: 0.96 },
  { track_id: 7, behaviour: 'Approaching Restricted Area', start_time: 31, end_time: 41, confidence: 0.92 },
  { track_id: 7, behaviour: 'Restricted Area Entry', start_time: 42, end_time: 55, confidence: 0.94 },
  { track_id: 7, behaviour: 'Stationary in Restricted Zone', start_time: 55, end_time: 61, confidence: 0.90 },
  { track_id: 7, behaviour: 'Exited Area', start_time: 62, end_time: 75, confidence: 0.88 },
  { track_id: 9, behaviour: 'Walking Quickly', start_time: 95, end_time: 110, confidence: 0.94 },
  { track_id: 9, behaviour: 'Possible Fall / Sudden Slip', start_time: 111, end_time: 126, confidence: 0.91 },
  { track_id: 9, behaviour: 'Lying on Floor', start_time: 126, end_time: 140, confidence: 0.89 },
];

export const MOCK_EVENTS: Event[] = [
  {
    event_id: 'EVT001',
    track_id: 7,
    event_type: 'Restricted Area Entry',
    start_time: 42,
    end_time: 55,
    confidence: 0.94,
    severity: 'high',
    reason: 'Person entered the predefined restricted zone without safety clearance.',
    evidence_url: 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=42,55',
  },
  {
    event_id: 'EVT002',
    track_id: 3,
    event_type: 'Prolonged Inactivity',
    start_time: 74,
    end_time: 98,
    confidence: 0.88,
    severity: 'medium',
    reason: 'Entity remained stationary inside active machinery zone beyond the 20s safety limit.',
    evidence_url: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=74,98',
  },
  {
    event_id: 'EVT003',
    track_id: 9,
    event_type: 'Possible Fall',
    start_time: 111,
    end_time: 126,
    confidence: 0.91,
    severity: 'high',
    reason: 'Sudden vertical displacement followed by static horizontal posture detected.',
    evidence_url: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=111,126',
  },
  {
    event_id: 'EVT004',
    track_id: 1,
    event_type: 'Perimeter Loitering',
    start_time: 15,
    end_time: 35,
    confidence: 0.79,
    severity: 'low',
    reason: 'Entity observed pacing along outer facility fence for over 20 seconds.',
    evidence_url: 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=15,35',
  },
];


export const MOCK_TIMELINE: TimelineEntry[] = [
  {
    timestamp: 15,
    formatted_time: '00:15',
    track_id: 1,
    label: 'Perimeter Loitering',
    type: 'event',
    severity: 'low',
    description: 'Person #1 observed pacing along outer facility fence.',
  },
  {
    timestamp: 31,
    formatted_time: '00:31',
    track_id: 7,
    label: 'Approaching Restricted Area',
    type: 'behaviour',
    description: 'Person #7 moving towards hazardous containment boundary.',
  },
  {
    timestamp: 42,
    formatted_time: '00:42',
    track_id: 7,
    label: 'Restricted Area Entry',
    type: 'event',
    severity: 'high',
    description: 'Person #7 breached predefined restricted zone.',
  },
  {
    timestamp: 74,
    formatted_time: '01:14',
    track_id: 3,
    label: 'Prolonged Inactivity',
    type: 'event',
    severity: 'medium',
    description: 'Person #3 stationary inside active machinery zone.',
  },
  {
    timestamp: 111,
    formatted_time: '01:51',
    track_id: 9,
    label: 'Possible Fall Detected',
    type: 'event',
    severity: 'high',
    description: 'Person #9 experienced sudden drop to floor.',
  },
];

export const MOCK_ANALYTICS: SystemAnalytics = {
  people_detected: 14,
  active_tracks: 4,
  normal_events: 52,
  abnormal_events: 4,
  high_risk_events: 2,
  events_by_type: [
    { name: 'Restricted Area Entry', count: 1 },
    { name: 'Prolonged Inactivity', count: 1 },
    { name: 'Possible Fall', count: 1 },
    { name: 'Perimeter Loitering', count: 1 },
  ],
  events_by_severity: [
    { severity: 'high', count: 2 },
    { severity: 'medium', count: 1 },
    { severity: 'low', count: 1 },
  ],
  activity_over_time: [
    { time: '00:00', count: 4, abnormal: 0 },
    { time: '00:30', count: 8, abnormal: 1 },
    { time: '01:00', count: 12, abnormal: 1 },
    { time: '01:30', count: 9, abnormal: 1 },
    { time: '02:00', count: 5, abnormal: 1 },
    { time: '02:30', count: 2, abnormal: 0 },
  ],
  behaviour_distribution: [
    { behaviour: 'Walking', count: 28 },
    { behaviour: 'Stationary', count: 14 },
    { behaviour: 'Approaching Boundary', count: 6 },
    { behaviour: 'Restricted Entry', count: 1 },
    { behaviour: 'Fall / Slip', count: 1 },
  ],
};

export const MOCK_ANALYSIS_STATUS: AnalysisStatus = {
  video_id: 'vid-autovision-001',
  status: 'completed',
  progress: 100,
  current_step: 'Analysis completed successfully',
  started_at: '2026-10-07T09:30:10Z',
  completed_at: '2026-10-07T09:31:05Z',
};

export const MOCK_ZONES: Zone[] = [
  {
    zone_id: 'ZONE-001',
    video_id: 'vid-autovision-001',
    name: 'Restricted Hazardous Enclosure',
    zone_type: 'restricted',
    coordinates: [
      [28, 22],
      [68, 22],
      [68, 78],
      [28, 78],
    ],
    color: '#f43f5e',
    enabled: true,
  },
  {
    zone_id: 'ZONE-002',
    video_id: 'vid-autovision-001',
    name: 'Outer Perimeter Caution Buffer',
    zone_type: 'caution',
    coordinates: [
      [15, 12],
      [85, 12],
      [85, 88],
      [15, 88],
    ],
    color: '#fbbf24',
    enabled: true,
  },
];

export const MOCK_EVIDENCE: EvidenceRecord[] = [
  {
    evidence_id: 'EVD-001',
    event_id: 'EVT001',
    video_id: 'vid-autovision-001',
    timestamp: 42,
    image_url: 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=42,55',
    resolution: '1920x1080',
    file_size_bytes: 4820120,
    created_at: '2026-10-07T09:30:42Z',
  },
  {
    evidence_id: 'EVD-002',
    event_id: 'EVT002',
    video_id: 'vid-autovision-001',
    timestamp: 74,
    image_url: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80',
    clip_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4#t=74,98',
    resolution: '1920x1080',
    file_size_bytes: 5210400,
    created_at: '2026-10-07T09:31:14Z',
  },
];

