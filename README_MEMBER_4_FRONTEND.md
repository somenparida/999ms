# Member 4 — Frontend Dashboard & Interactive Visualization Guide

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

Welcome Member 4! This guide provides the complete documentation, design specification, API contracts, and AI prompt to build the interactive **Frontend Dashboard**.

The dashboard connects directly to the **Member 3 FastAPI Backend** running at `http://localhost:8000/api`.

---

## 🎨 Technology Stack Recommendations

- **Framework**: React 18+ (Vite) or Next.js 14+
- **Styling**: Tailwind CSS + Lucide Icons / Tabler Icons
- **Canvas Overlay**: HTML5 `<canvas>` / Konva.js for dynamic bounding box & trajectory rendering over `<video>` player
- **State Management / Data Fetching**: Axios / TanStack Query (React Query)
- **Charts / Visuals**: Recharts or Chart.js for timeline and risk trend analytics

---

## 📡 API Endpoints Consumed by Member 4

Base URL: `http://localhost:8000/api`

### 1. Video Management
- `POST /api/videos/upload` (FormData file) → Upload video file
- `GET /api/videos` → List all uploaded videos
- `GET /api/videos/{video_id}` → Get single video details
- `DELETE /api/videos/{video_id}` → Delete video

### 2. Live Analysis Job Status
- `POST /api/videos/{video_id}/analyze` → Start video analysis job
- `GET /api/videos/{video_id}/analysis` → Get live processing stage & percentage
- `POST /api/videos/{video_id}/analysis/cancel` → Cancel active analysis job

### 3. Summary & KPI Metrics
- `GET /api/videos/{video_id}/summary` → Returns:
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

### 4. Chronological Timeline
- `GET /api/videos/{video_id}/timeline` → Returns:
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

### 5. Security Alerts & Event Feed
- `GET /api/videos/{video_id}/events` → List abnormal security events
- `GET /api/events/{event_id}` → Get single event details
- `PATCH /api/events/{event_id}` (Body: `{ "status": "reviewed" | "confirmed" | "dismissed" }`) → Update alert status

### 6. Evidence Drawer & Explainability
- `GET /api/events/{event_id}/evidence` → Returns evidence array:
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

### 7. Object Tracks & Trajectory Visualizer
- `GET /api/videos/{video_id}/tracks` → List all detected entity tracks
- `GET /api/videos/{video_id}/tracks/{track_id}/positions` → Returns position time-series

### 8. Zone Configurator
- `POST /api/zones` → Create restricted/monitored zone polygon
- `GET /api/videos/{video_id}/zones` → Get zones for video

---

## 🎨 Theme & Color System

- **Background**: `#0D1117` (Dark Cyber Gray)
- **Cards & Containers**: `#161B22` with `#21262D` borders and backdrop blur.
- **Severity Colors**:
  - 🔴 **CRITICAL**: `#FF3366` (`bg-red-500/10 border-red-500/50 text-red-400`)
  - 🟠 **HIGH**: `#FF9900` (`bg-orange-500/10 border-orange-500/50 text-orange-400`)
  - 🟡 **MEDIUM**: `#FFCC00` (`bg-yellow-500/10 border-yellow-500/50 text-yellow-400`)
  - 🔵 **LOW**: `#00CCFF` (`bg-cyan-500/10 border-cyan-500/50 text-cyan-400`)
  - 🟢 **NORMAL**: `#10B981` (`bg-emerald-500/10 border-emerald-500/50 text-emerald-400`)

---

## 🤖 AI Prompt to Generate Frontend Code

Copy and paste the prompt below into an AI coding assistant (e.g. Antigravity, Cursor, ChatGPT, Claude) to automatically generate the dashboard codebase:

```text
You are an expert Principal Frontend Engineer building the interactive Dashboard UI for HNX26PSI07: Autonomous Vision & Behaviour Understanding.

Your goal is to build a sleek, high-performance web dashboard (React / Next.js / Vite + Tailwind CSS) connecting to the backend at http://localhost:8000/api.

Features to Build:
1. Header bar with Video Dropdown selector, Upload Video modal, and live System Health badge polling GET /health.
2. KPI Metrics Grid displaying 7 Summary Cards from GET /api/videos/{video_id}/summary.
3. Video Player with HTML5 Canvas overlay rendering bounding boxes [x, y, w, h] synchronized with video timestamp.
4. Live Analysis Progress bar polling GET /api/videos/{video_id}/analysis.
5. Security Alert Feed displaying events from GET /api/videos/{video_id}/events with severity badges and status actions (PATCH /api/events/{event_id}).
6. Evidence Drawer modal displaying WHO, WHAT, WHEN, CONFIDENCE, WHY, bounding box coordinates, and trajectory path from GET /api/events/{event_id}/evidence.
7. Timeline Feed from GET /api/videos/{video_id}/timeline with click-to-seek video functionality.
8. Zone Configurator tool connecting to POST /api/zones and GET /api/videos/{video_id}/zones.
```
