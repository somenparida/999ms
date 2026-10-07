# Team Integration Guide — What to Share with Teammates

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

This document outlines exactly what **Member 3 (Backend & Integration)** shares with **Member 1**, **Member 2**, and **Member 4** to integrate the entire system.

---

## 📌 Section 1: What to Share with Member 1 (Object Detection & Tracking)

Member 1 generates detected objects and tracking IDs. They send track data to your backend API.

### 1. Backend Endpoint to Share:
`POST http://localhost:8000/api/videos/{video_id}/tracks/import`

### 2. Request Contract Format (JSON Body):
```json
{
  "tracks": [
    {
      "track_id": 7,
      "object_type": "person",
      "timestamp": 42.31,
      "frame_number": 1269,
      "bbox": [120, 80, 220, 350],
      "center": [170, 215],
      "confidence": 0.94,
      "velocity": 0.2
    }
  ]
}
```

### 3. Key Notes for Member 1:
- `video_id` is the ID of the uploaded video in PostgreSQL.
- `bbox` format can be `[x, y, width, height]` or `[x1, y1, x2, y2]`.
- Submit track positions as frames are processed. Multiple calls for the same `(track_id, frame_number)` are idempotent.

---

## 📌 Section 2: What to Share with Member 2 (Behaviour Analysis & Anomaly Detection)

Member 2 analyzes object tracks and determines behavior classifications (`normal` vs `abnormal`). They send behavior predictions to your backend API.

### 1. Backend Endpoint to Share:
`POST http://localhost:8000/api/videos/{video_id}/behaviours/import`

### 2. Request Contract Format (JSON Body):
```json
{
  "behaviours": [
    {
      "track_id": 7,
      "behaviour_type": "restricted_area_entry",
      "start_time": 42.31,
      "end_time": 55.82,
      "confidence": 0.94,
      "classification": "abnormal",
      "reason": "Person #7 crossed restricted zone boundary."
    },
    {
      "track_id": 3,
      "behaviour_type": "walking",
      "start_time": 12.20,
      "end_time": 25.40,
      "confidence": 0.92,
      "classification": "normal",
      "reason": "Standard walking trajectory along pathway."
    }
  ]
}
```

### 3. Key Notes for Member 2:
- `classification`: must be either `"normal"` or `"abnormal"`.
- When `classification == "abnormal"`, Member 3's backend automatically creates a security **Event**, assigns severity (`low`, `medium`, `high`, `critical`), and generates **Evidence** items (bounding box & trajectory path).

---

## 📌 Section 3: What to Share with Member 4 (Frontend Dashboard & Visualization)

Member 4 builds the interactive UI dashboard. They consume GET/POST/PATCH endpoints from your backend.

### 1. Interactive Swagger Documentation Link:
`http://localhost:8000/docs`

### 2. Documentation Files to Share:
- [README_MEMBER_4_FRONTEND.md](file:///home/frost/hacknex/README_MEMBER_4_FRONTEND.md)
- [MEMBER_4_FRONTEND_PROMPT.md](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md)

### 3. API Endpoints Member 4 Consumes:
- **Health Check**: `GET /health`
- **Video Management**: `POST /api/videos/upload`, `GET /api/videos`, `GET /api/videos/{id}`, `DELETE /api/videos/{id}`
- **Analysis Job Progress**: `POST /api/videos/{id}/analyze`, `GET /api/videos/{id}/analysis`
- **Dashboard KPI Summary**: `GET /api/videos/{id}/summary`
- **Chronological Timeline**: `GET /api/videos/{id}/timeline`
- **Security Alert Feed**: `GET /api/videos/{id}/events`, `PATCH /api/events/{id}`
- **Evidence Drawer**: `GET /api/events/{id}/evidence`
- **Track & Trajectory Positions**: `GET /api/videos/{id}/tracks`, `GET /api/videos/{id}/tracks/{track_id}/positions`
- **Zone Configurator**: `POST /api/zones`, `GET /api/videos/{id}/zones`
