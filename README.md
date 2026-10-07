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
