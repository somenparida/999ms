# Autonomous Vision & Behaviour Understanding — Backend

**Member 3 Subsystem | HNX26PSI07 | HackNex 2026**

> FastAPI + PostgreSQL + SQLAlchemy + Alembic integration backbone connecting Object Detection & Tracking (Member 1), Behaviour Intelligence (Member 2), and Interactive Dashboard UI (Member 4) into one coherent system.

---

## 📌 Executive Summary

The **Backend & Integration Subsystem (Member 3)** acts as the central single source of truth for the entire application. It decouples machine learning modules from hardware and UI details by providing stable, validated data contracts.

```text
  Member 1 (Detection & Tracking)
                ↓
    POST /api/videos/{id}/tracks/import
                ↓
            Member 3 (FastAPI + PostgreSQL)
                ↓
  Member 2 (Behaviour Intelligence)
                ↓
  POST /api/videos/{id}/behaviours/import
                ↓
     Automated Event Generation Engine
                ↓
        Evidence & Timeline Generator
                ↓
  Member 4 (Frontend Dashboard)
```

---

## ⚡ Core Features & Capabilities

- **Video Storage & Processing Lifecycle**: Upload video files to disk storage (`storage/videos`), track resolution, frame rate, duration, and manage live analysis job status (`queued`, `video_processing`, `detection`, `tracking`, `behaviour_analysis`, `completed`, `failed`).
- **PostgreSQL & SQLAlchemy Relational Engine**: Relational schema covering `Video`, `Track`, `TrackPosition`, `Behaviour`, `Event`, `Evidence`, `AnalysisJob`, and `Zone`.
- **Member 1 Integration (Tracking Data)**: Idempotent bulk import of object bounding boxes (`[x, y, w, h]` or `[x1, y1, x2, y2]`), frame timestamps, velocities, and 17 COCO pose keypoint skeletons.
- **Member 2 Integration (Behaviour Intelligence)**: Receives activity classifications (`STANDING`, `WALKING`, `RUNNING`, `SITTING`, `CROUCHING`, `BENDING`, `LYING`, `FALLING`), posture durations, transitions, and normality ratings (`NORMAL`, `POTENTIALLY_UNUSUAL`, `ABNORMAL`).
- **Automated Security Event Engine**: Automatically converts abnormal behaviors into structured alerts with severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and deduplication logic.
- **Explainable Evidence Generation**: Automatically attaches multi-type evidence items: Bounding Box location, Trajectory path coordinates, and 17-Keypoint Skeleton Pose data.
- **Dashboard & Timeline Aggregations (Member 4)**: Calculates 7 real-time KPI metrics (People Detected, Unique Tracks, Normal Events, Abnormal Events, High-Risk Events, Average Confidence %, Duration) and chronological timeline feeds.
- **Restricted Zone Configurator**: CRUD polygon boundaries for spatial rule checking.
- **Multi-Laptop Networking & CORS Support**: Configured to run across different laptops on the same Wi-Fi network or over public tunnels (`ngrok`).
- **Automated Test Suite**: 8 comprehensive `pytest` test suites verifying unit logic, API endpoints, idempotency, and full end-to-end integration flows.

---

## 🚀 Quickstart & Setup

### 1. Environment Configuration

Copy the sample environment file:

```bash
cp .env.example .env
```

Default configuration in `.env`:
```env
DATABASE_URL=sqlite:///./vision_behaviour.db
UPLOAD_DIR=./storage/videos
OUTPUT_DIR=./storage/processed
EVIDENCE_DIR=./storage/evidence
CORS_ORIGINS=["*"]
DEBUG=true
```

### 2. Run Server Locally (SQLite / Dev Mode)

Install dependencies and start Uvicorn with auto-IP output:

```bash
pip install -r requirements.txt
./start_server.sh
```

Or start manually with Uvicorn:

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **System Health Check**: `http://localhost:8000/health`

### 3. Run with Docker Compose (PostgreSQL 15 + FastAPI)

To launch production-grade PostgreSQL 15 container alongside the backend:

```bash
docker compose up --build
```

PostgreSQL database will run on port `5432` and backend API on port `8000`.

---

## 🌐 Connecting Teammates Across Laptops

When team members are on different laptops on the same Wi-Fi / Hotspot:

1. Find your local IP address (`hostname -I`).
2. Run `./start_server.sh` (or `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`).
3. Teammates connect using `http://<YOUR_LOCAL_IP>:8000`:

| Teammate | Endpoint / Contract |
| :--- | :--- |
| **Member 1 (Tracking)** | `POST http://<YOUR_IP>:8000/api/videos/{video_id}/tracks/import` |
| **Member 2 (Behaviour)** | `POST http://<YOUR_IP>:8000/api/videos/{video_id}/behaviours/import` |
| **Member 4 (Frontend)** | Base URL: `http://<YOUR_IP>:8000/api` |
| **Swagger Docs** | `http://<YOUR_IP>:8000/docs` |

*For detailed networking instructions, see [`README_MULTI_LAPTOP_CONNECT.md`](file:///home/frost/hacknex/README_MULTI_LAPTOP_CONNECT.md).*

---

## 📡 API Reference Summary

### Videos & Analysis
- `POST /api/videos/upload` — Upload MP4 video file
- `GET /api/videos` — List all uploaded videos
- `GET /api/videos/{id}` — Get single video details
- `DELETE /api/videos/{id}` — Delete video
- `POST /api/videos/{id}/analyze` — Start analysis job
- `GET /api/videos/{id}/analysis` — Poll analysis progress percentage & current stage

### Member 1: Track Import
- `POST /api/videos/{id}/tracks/import` — Import track positions & 17 COCO keypoints
- `GET /api/videos/{id}/tracks` — Get all detected tracks
- `GET /api/videos/{id}/tracks/{track_id}/positions` — Get position time-series

### Member 2: Behaviour Import
- `POST /api/videos/{id}/behaviours/import` — Import activity classifications & triggers Event Engine
- `GET /api/videos/{id}/behaviours` — List behaviours

### Events & Evidence
- `GET /api/videos/{id}/events` — List abnormal security events
- `GET /api/events/{id}` — Get single event details
- `PATCH /api/events/{id}` — Update event status (`reviewed`, `confirmed`, `dismissed`)
- `GET /api/events/{id}/evidence` — Get bounding box, trajectory, and skeleton keypoints evidence

### Member 4: Dashboard Aggregations
- `GET /api/videos/{id}/summary` — Fetch 7 KPI metrics
- `GET /api/videos/{id}/timeline` — Fetch chronological timestamped activity feed
- `POST /api/zones` / `GET /api/videos/{id}/zones` — Create & list restricted zone polygons

---

## 🧪 Testing Suite

Run all unit, API, and integration test suites:

```bash
pytest -v
```

Includes End-to-End integration test (`tests/test_integration.py`) verifying:
$$\text{Video Upload} \rightarrow \text{Track Import} \rightarrow \text{Behaviour Import} \rightarrow \text{Auto Event Generation} \rightarrow \text{Evidence Attachment} \rightarrow \text{Dashboard API Retrieval}$$

---

## 🎨 Member 4 Frontend AI Prompt

For Member 4 to generate the dynamic React/Next.js/Vite frontend dashboard using AI coders, refer to:
- Prompt Guide: [`MEMBER_4_FRONTEND_PROMPT.md`](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md)
- Frontend Spec: [`README_MEMBER_4_FRONTEND.md`](file:///home/frost/hacknex/README_MEMBER_4_FRONTEND.md)
