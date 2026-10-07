# HNX26PSI07 — Autonomous Vision & Behaviour Understanding

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=for-the-badge&logo=docker)
![Pytest](https://img.shields.io/badge/Pytest-9--Passed-46A2F1.svg?style=for-the-badge&logo=pytest)
![HackNex 2026](https://img.shields.io/badge/HackNex-2026-orange.svg?style=for-the-badge)

Welcome to the central integration repository for **HackNex 2026 — Track HNX26PSI07: Autonomous Vision & Behaviour Understanding**.

This repository contains the complete **FastAPI + PostgreSQL + SQLAlchemy + Alembic** backend, event generation engine, explainable evidence manager, multi-laptop networking configuration, automated test suite, and team integration documentation connecting all 4 team members into a single unified platform.

---

## 📂 Repository Structure & Overview

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

### 1. Start Server Locally (Auto-IP Hotspot Mode)
```bash
cd backend
./start_server.sh
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

## 🤝 Team Member Roles & Integration Matrix

| Team Member | Subsystem Role | Endpoint / Contract |
| :--- | :--- | :--- |
| **Member 1** | Object Detection & Tracking (YOLOv8/11 + ByteTrack) | `POST /api/videos/{video_id}/tracks/import` |
| **Member 2** | Behaviour Intelligence (Posture & Fall Reasoning) | `POST /api/videos/{video_id}/behaviours/import` |
| **Member 3** | Backend & Integration Layer (FastAPI + PostgreSQL) | Central API Engine (`http://10.89.105.218:8000/api`) |
| **Member 4** | Interactive Frontend Dashboard UI (React Canvas Overlay) | Base API: `http://10.89.105.218:8000/api` |

---

## 📘 Comprehensive Technical Documentation Links

- 📖 **Backend Architecture & API Specs**: [`backend/README.md`](file:///home/frost/hacknex/backend/README.md)
- 🤝 **Team Integration Guide**: [`README_TEAM_INTEGRATION.md`](file:///home/frost/hacknex/README_TEAM_INTEGRATION.md)
- 📱 **Multi-Laptop Networking & Hotspot Guide**: [`README_MULTI_LAPTOP_CONNECT.md`](file:///home/frost/hacknex/README_MULTI_LAPTOP_CONNECT.md)
- 🖥️ **Member 4 Frontend Dashboard Guide**: [`README_MEMBER_4_FRONTEND.md`](file:///home/frost/hacknex/README_MEMBER_4_FRONTEND.md)
- 🤖 **Member 4 AI Prompt Guide**: [`backend/MEMBER_4_FRONTEND_PROMPT.md`](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md)
