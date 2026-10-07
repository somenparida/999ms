# Member 3 — Backend, PostgreSQL & Integration Layer

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

This repository contains the complete backend and integration layer connecting Member 1 (Detection & Tracking), Member 2 (Behaviour Analysis & Anomaly Detection), Member 3 (Backend & Persistence), and Member 4 (Frontend Dashboard).

---

## 🚀 Getting Started

### 1. Environment Setup

Create `.env` file or use defaults:

```bash
cp .env.example .env
```

### 2. Local Execution (SQLite / PostgreSQL)

Install dependencies and run Uvicorn dev server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Access Swagger UI: `http://localhost:8000/docs`
Access Healthcheck: `http://localhost:8000/health`

### 3. Docker Deployment

Run complete environment with PostgreSQL and FastAPI container:

```bash
docker compose up --build
```

---

## 🧪 Testing

Run test suite with pytest:

```bash
pytest
```

Includes end-to-end integration test (`tests/test_integration.py`):
`Track Data -> Behaviour Data -> Event Generation -> Evidence Attachment -> API Retrieval`.

---

## 📡 API Contracts

### Member 1: Track Import
`POST /api/videos/{video_id}/tracks/import`

### Member 2: Behaviour Import
`POST /api/videos/{video_id}/behaviours/import`

### Member 4: Dashboard Endpoints
- `GET /api/videos/{video_id}/timeline`
- `GET /api/videos/{video_id}/summary`
- `GET /api/videos/{video_id}/events`
- `GET /api/events/{event_id}/evidence`

---

## 🎨 Member 4 — Frontend Dashboard AI Prompt

To build the dynamic frontend dashboard for Member 4 using AI agents (React, Next.js, or Vite + Tailwind CSS), pass the complete system prompt stored in [`MEMBER_4_FRONTEND_PROMPT.md`](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md):

```text
You are an expert Principal Frontend Engineer building the interactive Dashboard UI for HNX26PSI07: Autonomous Vision & Behaviour Understanding.

Your goal is to build a sleek, high-performance web dashboard (React / Next.js / Vite + Tailwind CSS) that connects directly to the Member 3 FastAPI + PostgreSQL backend running at http://localhost:8000/api.

Key Dashboard Features to Implement:
1. Video Upload & Player Canvas: Drag & drop upload, HTML5 player with dynamic canvas bounding box overlay synchronized with video timestamp.
2. KPI Metric Cards: Display statistics from GET /api/videos/{video_id}/summary (People Detected, Unique Tracks, Normal Events, Abnormal Events, High-Risk Events, Avg Confidence, Duration).
3. Live Analysis Progress Bar: Poll GET /api/videos/{video_id}/analysis showing live percentage and active stage.
4. Security Alerts Feed: Display events from GET /api/videos/{video_id}/events with severity badges (CRITICAL, HIGH, MEDIUM, LOW) and status update actions (PATCH /api/events/{event_id}).
5. Evidence Drawer: Modal showing WHO, WHAT, WHEN, CONFIDENCE, WHY, bounding box coordinates, and trajectory path from GET /api/events/{event_id}/evidence.
6. Chronological Timeline: Interactive feed from GET /api/videos/{video_id}/timeline with click-to-seek video playback.
7. Zone Configurator: Interactive zone polygon manager connecting to POST /api/zones and GET /api/videos/{video_id}/zones.
```

