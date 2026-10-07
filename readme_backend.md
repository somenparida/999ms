# HNX26PSI07 — Autonomous Vision & Behaviour Understanding

## Backend, PostgreSQL & Integration Subsystem (Member 3)

Welcome to the central integration repository for **HackNex 2026 — Autonomous Vision & Behaviour Understanding**.

This repository contains the complete **FastAPI + PostgreSQL + SQLAlchemy + Alembic** backend, event generation engine, evidence manager, multi-laptop networking configuration, test suite, and integration documentation connecting all 4 team members into a single unified platform.

---

## 📂 Repository Structure

```text
.
├── backend/                        # Complete FastAPI + PostgreSQL Backend Application
│   ├── app/
│   │   ├── api/                    # REST API Routers (Videos, Tracks, Behaviours, Events, Evidence, Analysis, Zones, Health)
│   │   ├── core/                   # Settings, Config & Logging
│   │   ├── db/                     # SQLAlchemy Session & Declarative Base
│   │   ├── models/                 # ORM Models (Video, Track, TrackPosition, Behaviour, Event, Evidence, AnalysisJob, Zone)
│   │   ├── schemas/                # Pydantic Validation Schemas & Data Contracts
│   │   ├── services/               # Business Logic, Event Engine & Aggregations
│   │   └── main.py                 # FastAPI Main Application
│   ├── migrations/                 # Alembic Database Migrations
│   ├── mock/                       # Realistic Datasets (tracks.json, behaviours.json, events.json)
│   ├── storage/                    # Disk Storage (videos, processed, evidence, event_clips)
│   ├── tests/                      # Pytest Unit & End-to-End Integration Suite
│   ├── Dockerfile                  # Container definition for FastAPI app
│   ├── docker-compose.yml          # Services setup (PostgreSQL 15 + FastAPI app)
│   ├── start_server.sh             # Multi-laptop IP auto-detection startup script
│   ├── MEMBER_4_FRONTEND_PROMPT.md # AI Prompt to generate Member 4's Frontend Dashboard
│   └── README.md                   # Backend Technical Documentation
├── README_TEAM_INTEGRATION.md      # Integration Guide for Member 1, Member 2, and Member 4
├── README_MEMBER_4_FRONTEND.md     # Frontend Dashboard Guide & Specifications
├── README_MULTI_LAPTOP_CONNECT.md  # Multi-laptop networking guide (Wi-Fi IP & ngrok tunneling)
├── README_BEHAVIOUR.md             # Member 2 Subsystem Specification
└── README_OBJECT.md                # Member 1 Subsystem Specification
```

---

## ⚡ Quickstart: Run Backend Server

### 1. Start Server Locally
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### 2. Start with Docker Compose (PostgreSQL 15)
```bash
cd backend
docker compose up --build
```

### 3. Run Test Suite
```bash
cd backend
pytest -v
```

---

## 🤝 Team Integration Summary

| Team Member | Subsystem Role | API Endpoint / Contract |
| :--- | :--- | :--- |
| **Member 1** | Object Detection & Tracking | `POST /api/videos/{video_id}/tracks/import` |
| **Member 2** | Behaviour Intelligence | `POST /api/videos/{video_id}/behaviours/import` |
| **Member 3** | Backend & Integration Layer | Central FastAPI + PostgreSQL Engine |
| **Member 4** | Interactive Frontend Dashboard | Base API: `http://<YOUR_IP>:8000/api` |

For detailed integration instructions, read [README_TEAM_INTEGRATION.md](file:///home/frost/hacknex/README_TEAM_INTEGRATION.md) and [README_MULTI_LAPTOP_CONNECT.md](file:///home/frost/hacknex/README_MULTI_LAPTOP_CONNECT.md).

---

## 🖥️ Member 4 — Interactive Frontend & Telemetry Dashboard (Delivered UI)

The frontend application provides the primary command-and-control interface for the AUTOVISION platform. Below is the visual and functional analysis of the delivered user interface as documented in the `screenshots/` directory:

### 1. Security & Behavioral Telemetry Dashboard
![Security & Behavioral Telemetry Dashboard](screenshots/Screenshot%202026-10-07%20162736.png)

- **Route**: `/dashboard`
- **Backend Endpoints Consumed**: `GET /api/videos`, `GET /api/videos/{id}/status`, `GET /api/videos/{id}/events`, `GET /api/analytics`
- **Key Capabilities**:
  - **Live Video Feed Banner**: Displays current active surveillance feed (`Surveillance Feed - Sector 4 Industrial Gate`, `1920x1080 @ 30 FPS`, duration: `2m 31s`), with real-time pipeline status (`COMPLETED | 100%`) and direct "Inspect Feed" shortcut.
  - **KPI Telemetry Cards**:
    - **People Detected**: Ingested camera stream entities (`14`, with `+2 new`).
    - **Active Tracks**: DeepSORT track IDs currently tracked in active memory (`4`).
    - **Normal Events**: Baseline compliant movements (`52`, `92.8% Nominal`).
    - **Abnormal Events**: Flagged supervisor alerts (`4`, `Action Required`).
    - **High-Risk Events**: Critical security breaches requiring immediate intervention (`2`).
  - **Recent Abnormal Events Stream**: High-priority alert queue displaying entity IDs, timestamps, confidence scores (`94%`), severity badges, and classification rationale.
  - **Event Distribution Breakdown**: Horizontal frequency chart across event classes (`Restricted Area Entry`, `Prolonged Inactivity`, `Possible Fall`, `Perimeter Loitering`).

---

### 2. Track Explorer & DeepSORT Entity Dossiers
![Track Explorer & Entity Dossiers](screenshots/Screenshot%202026-10-07%20162748.png)

- **Route**: `/tracks`
- **Backend Endpoints Consumed**: `GET /api/videos/{id}/tracks`, `GET /api/videos/{id}/behaviours`, `GET /api/videos/{id}/events`
- **Key Capabilities**:
  - **Track Index & Filter**: Searchable directory of all DeepSORT allocated track IDs (e.g., Person #1, Person #3, Person #7) with individual lifespan spans, average detection confidence, and alert counters.
  - **Forensic Entity Dossier**:
    - First Detected & Last Detected timestamps (`00:13` to `01:02`).
    - Total track duration (`49s`) and mean confidence (`94%`).
  - **Associated Security Breaches**: Direct linkage to generated abnormal event records (e.g., `EVT001` Restricted Area Entry).
  - **Sequential Behaviour Timeline**: Granular state transition logs with duration per state (`Walking` 17s → `Approaching Restricted Area` 10s → `Restricted Area Entry` 13s) and anomaly phase highlighting.

---

### 3. System Analytics & Anomaly Rate Forensics
![System Analytics & Behavior Forensics](screenshots/Screenshot%202026-10-07%20162759.png)

- **Route**: `/analytics`
- **Backend Endpoints Consumed**: `GET /api/analytics`
- **Key Capabilities**:
  - **Temporal Activity & Breach Frequency Area Chart**: Dual-curve temporal visualization displaying `Total Ingested Entities` (cyan) versus `Abnormal Breaches` (rose) across 30-second time intervals.
  - **Risk Tier Breakdown Donut Chart**: Multi-tier security risk proportion analysis classifying incidents into `HIGH RISK`, `MEDIUM RISK`, and `LOW RISK`.
  - **Live Aggregation Stats**: Real-time totals for people detected, active trajectories, and baseline compliance rates.

---

### 4. Architecture Control, Thresholds & Multi-Laptop Gateway
![System Settings & Architecture Control](screenshots/Screenshot%202026-10-07%20162810.png)

- **Route**: `/settings`
- **Backend Endpoints Consumed**: `GET /health`, `POST /api/videos/{id}/tracks/import`, `POST /api/videos/{id}/behaviours/import`
- **Key Capabilities**:
  - **Detection & Anomaly Thresholds**: Interactive slider controls for YOLOv8 detection confidence (`0.65`), temporal behaviour sensitivity (`0.75`), and alert escalation thresholds (`0.80`).
  - **Multi-Laptop Network & Gateway Manager**:
    - Configurable base URL input for Member 3's Wi-Fi LAN IP (`http://192.168.x.x:8000`) or ngrok tunnel.
    - Quick-select presets (`localhost:8000`, `Wi-Fi LAN IP`, `ngrok Tunnel`).
    - Real-time round-trip latency ping test against the FastAPI `/health` endpoint.
    - Mode toggle between **Standalone Mock Engine** (fail-safe offline demo) and **Live FastAPI Backend**.
    - Direct link to interactive Swagger Documentation (`/docs`).
  - **4-Person Team Integration Architecture Matrix**: Visual telemetry showing contract readiness across Member 1 (`Track[]`), Member 2 (`Behaviour[]`), Member 3 (`Event[]`), and Frontend (`Verified`).
