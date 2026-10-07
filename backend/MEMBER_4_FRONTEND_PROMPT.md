# Member 4 — Frontend Dashboard AI Prompt

Use this prompt with an AI assistant or development team to generate the complete, modern, interactive Frontend Dashboard for **HNX26PSI07 — Autonomous Vision & Behaviour Understanding**.

---

```text
You are an expert Principal Frontend Engineer building the interactive Dashboard UI for HNX26PSI07: Autonomous Vision & Behaviour Understanding.

Your goal is to build a sleek, high-performance web dashboard (React / Next.js / Vite + Tailwind CSS / Vanilla CSS) that connects directly to the Member 3 FastAPI + PostgreSQL backend running at `http://localhost:8000/api`.

---

### 🎨 Design System & Visual Aesthetics
1. **Theme**: Deep dark cyber-security theme (`#0D1117`, `#161B22`, `#21262D`) with glassmorphism cards, subtle glowing borders, and crisp typography (Inter or Outfit).
2. **Severity Color Palette**:
   - 🔴 **CRITICAL**: Glowing Neon Crimson (`#FF3366`, `bg-red-500/10 border-red-500/50 text-red-400`)
   - 🟠 **HIGH**: Vivid Amber (`#FF9900`, `bg-orange-500/10 border-orange-500/50 text-orange-400`)
   - 🟡 **MEDIUM**: Electric Yellow (`#FFCC00`, `bg-yellow-500/10 border-yellow-500/50 text-yellow-400`)
   - 🔵 **LOW**: Cyber Cyan (`#00CCFF`, `bg-cyan-500/10 border-cyan-500/50 text-cyan-400`)
   - 🟢 **NORMAL**: Emerald (`#10B981`, `bg-emerald-500/10 border-emerald-500/50 text-emerald-400`)
3. **Micro-Animations**: Smooth transitions on hover, pulse effects on live processing jobs, tab switches, and evidence modals.

---

### 📡 Backend API Contract (FastAPI at `http://localhost:8000`)

#### 1. Video Management
- `POST /api/videos/upload` (FormData: `file`) → returns `{ id, filename, original_filename, status, duration, fps }`
- `GET /api/videos` → returns list of video objects
- `GET /api/videos/{video_id}` → returns video details
- `DELETE /api/videos/{video_id}` → deletes video

#### 2. Analysis Job Progress
- `POST /api/videos/{video_id}/analyze` → starts analysis job `{ id, status: "processing", progress: 10.0, current_stage: "video_processing" }`
- `GET /api/videos/{video_id}/analysis` → returns current progress `%` and `current_stage`
- `POST /api/videos/{video_id}/analysis/cancel` → cancels running job

#### 3. Dashboard Summary & KPI Cards
- `GET /api/videos/{video_id}/summary` → returns:
  ```json
  {
    "people_detected": 12,
    "unique_tracks": 12,
    "normal_events": 31,
    "abnormal_events": 4,
    "high_risk_events": 2,
    "average_confidence": 0.91,
    "duration": 152.4
  }
  ```

#### 4. Chronological Timeline
- `GET /api/videos/{video_id}/timeline` → returns list of timestamped events/behaviours:
  ```json
  [
    {
      "timestamp": 12.2,
      "track_id": 3,
      "type": "walking",
      "classification": "normal"
    },
    {
      "timestamp": 42.3,
      "track_id": 7,
      "type": "restricted_area_entry",
      "classification": "abnormal",
      "event_id": 1,
      "severity": "high",
      "reason": "Person entered restricted zone."
    }
  ]
  ```

#### 5. Security Events & Alert Feed
- `GET /api/videos/{video_id}/events` → returns abnormal security events list
- `GET /api/events/{event_id}` → returns single event detail
- `PATCH /api/events/{event_id}` (Body: `{ "status": "reviewed" | "confirmed" | "dismissed" }`) → updates alert state

#### 6. Evidence Drawer & Explainability
- `GET /api/events/{event_id}/evidence` → returns evidence items (`bounding_box`, `trajectory`, `frame`, `video_clip`):
  ```json
  [
    {
      "id": 1,
      "evidence_type": "bounding_box",
      "timestamp": 42.31,
      "frame_number": 1269,
      "description": "Bounding box location at timestamp 42.31s",
      "metadata": {
        "bbox": [120, 80, 220, 350],
        "center": [170, 215],
        "confidence": 0.94
      }
    },
    {
      "id": 2,
      "evidence_type": "trajectory",
      "timestamp": 42.31,
      "frame_number": 1269,
      "description": "Track trajectory path containing 3 waypoints",
      "metadata": {
        "trajectory": [[130, 275, 12.2], [170, 215, 42.31], [200, 225, 55.82]]
      }
    }
  ]
  ```

#### 7. Track Visualizer & Time-Series
- `GET /api/videos/{video_id}/tracks` → returns all detected tracks
- `GET /api/videos/{video_id}/tracks/{track_id}/positions` → returns bounding box time-series `[x, y, w, h, timestamp, frame_number]`

#### 8. Restricted Zones Setup
- `POST /api/zones` (Body: `{ "video_id": 1, "name": "Zone A", "zone_type": "restricted", "coordinates": [[100,100],[400,100],[400,400],[100,400]] }`)
- `GET /api/videos/{video_id}/zones`

---

### 🖥️ Dashboard Page Layout Requirements

1. **Header Bar**:
   - System title: `HNX26PSI07 — Autonomous Vision & Behaviour Intelligence`
   - Active Video Selector dropdown & Upload Video modal button
   - Live Health Status Indicator polling `/health` (Green "System Operational").

2. **Top KPI Row**:
   - 7 Metric Cards: People Detected, Unique Tracks, Normal Behaviours, Abnormal Events, High-Risk Alerts, Avg Confidence, Duration.

3. **Main Content Grid (2 Columns)**:
   - **Left Column (Video & Player Canvas)**:
     - HTML5 Video Player with controls.
     - Canvas Overlay rendering bounding boxes and trajectory lines dynamically synchronized with current video timestamp (`video.currentTime`).
     - Live Analysis Progress Bar when job is active (with animated pulse and percentage count).
   - **Right Column (Tabs)**:
     - **Tab 1: Alert Feed**: Cards sorted by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`). Quick status update buttons (`Mark Reviewed`, `Confirm`, `Dismiss`). "Inspect Evidence" button opening Evidence Drawer.
     - **Tab 2: Timeline**: Chronological scrubber/feed with timestamp click-to-seek video player.
     - **Tab 3: Track Entities**: List of unique track IDs (Person #1, Person #7) with confidence ratings and bounding box positions.
     - **Tab 4: Zone Configurator**: Interactive polygon overlay builder to mark restricted zones.

4. **Evidence Inspection Modal/Drawer**:
   - Displays WHO (Track ID), WHAT (Event Type), WHEN (Timestamp), CONFIDENCE (%), WHY (Reason).
   - Visual Bounding Box coordinate breakdown `[X, Y, W, H]`.
   - Trajectory path visualization graph.
   - Annotated Evidence Frame image preview.
```
