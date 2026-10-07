# AUTOVISION — Autonomous Vision & Behaviour Understanding

[![HackNex 2026](https://img.shields.io/badge/HackNex-2026-orange.svg?style=flat-square)](https://hacknex.org/)
[![Problem Statement: HNX26PSI07](https://img.shields.io/badge/Track-HNX26PSI07-blueviolet.svg?style=flat-square)](README.md)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![YOLO11](https://img.shields.io/badge/YOLO11-Detection-00FFFF.svg?style=flat-square)](https://github.com/ultralytics/ultralytics)

Welcome to **AUTOVISION** (Warehouse Sentinel), an end-to-end intelligent surveillance platform built for **HackNex 2026 — Problem Statement HNX26PSI07: Autonomous Vision & Behaviour Understanding**. 

AUTOVISION integrates multi-person detection, trajectory tracking, explainable behavioral reasoning, automated safety hazard detection, forensic evidence logging, and a command-and-control frontend dashboard into a unified, modular architecture.

---

## 🏛️ End-to-End Pipeline Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │                      VIDEO INPUT                       │
       │       Continuous RTSP / MP4 Multi-Camera Streams       │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  MEMBER 1: Person Detection & Multi-Person Tracking                          │
│  • Pretrained YOLO11n object detector                                        │
│  • ByteTrack multi-entity tracking engine                                    │
│  • Persistent track_id, pixel bounding boxes [x1, y1, x2, y2], timestamps   │
│  • Integration Contract: POST /api/videos/{video_id}/tracks/import           │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  MEMBER 2: Behaviour Intelligence & Posture/Fall Reasoning                   │
│  • 8 Activity Classes: STANDING, WALKING, RUNNING, SITTING, CROUCHING,       │
│    BENDING, LYING, FALLING                                                   │
│  • Decoupled Normality Layer: NORMAL, POTENTIALLY_UNUSUAL, ABNORMAL          │
│  • Ergonomic Hazard Monitoring (Sustained Bending >30s, Inactivity >60s)     │
│  • 4-Phase Kinetic Fall Detection (Drop Rate -> Impact Spike -> Aspect Ratio)│
│  • CPU-Optimized (<0.5ms per update)                                         │
│  • Integration Contract: POST /api/videos/{video_id}/behaviours/import       │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  MEMBER 3: Backend, PostgreSQL & Incident Generation Engine                  │
│  • FastAPI REST API + SQLAlchemy ORM + Alembic Migrations                    │
│  • PostgreSQL 15 Relational Schema (Videos, Tracks, Positions, Events, Zones)│
│  • Automated Rule Engine: Geofenced Zone Violations & Severity Scoring       │
│  • Dual-Storage Evidence: Photographic Keyframes & .mp4 Incident Clips       │
│  • Central Gateway: http://<LAN_IP>:8000/api                                 │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  MEMBER 4: Interactive Command-and-Control Frontend (This App)               │
│  • React 19 + TypeScript + Vite + Tailwind CSS + Recharts                    │
│  • Video Intelligence Workspace with live HUD & Bounding Box Overlays        │
│  • Geofenced Safety Zone Overlays (Restricted, Caution, Safe)                │
│  • Forensic Event Dossiers with Dual Keyframe Image & .mp4 Video Player      │
│  • DeepSORT Track Explorer with Trajectory Coordinates Table (TrackPosition) │
│  • Multi-Laptop Wi-Fi Gateway Manager with Real-Time Ping Latency Check      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📸 Visual Tour of the Application

### 1. Security & Behavioral Telemetry Dashboard
Real-time command center displaying overall system status, active surveillance stream telemetry, aggregated KPI metrics, high-priority alert queues, and incident category distributions.

![Dashboard Preview](screenshots/Screenshot%202026-10-07%20162736.png)

- **Route**: `/dashboard`
- **Active Stream Banner**: Real-time camera metadata (`Surveillance Feed - Sector 4 Industrial Gate`, `1920x1080 @ 30 FPS`, `2m 31s`, `Status: COMPLETED | 100%`).
- **Telemetry Stat Cards**: Camera stream entities (`14`, `+2 new`), active DeepSORT tracks (`4`), baseline compliance (`52`, `92.8% Nominal`), abnormal supervisor alerts (`4`), and critical breaches (`2 Critical`).
- **Recent Abnormal Events Feed**: Immediate alert queue with entity IDs, confidence scores (`94%`), timestamps, and violation rationale.
- **Event Distribution Bar Chart**: Frequency breakdown across anomaly categories.

---

### 2. DeepSORT Track Explorer & Entity Dossiers
Detailed lifecycle inspection for any detected entity, tracking historical trajectories and state transitions over time.

![Track Explorer Preview](screenshots/Screenshot%202026-10-07%20162748.png)

- **Route**: `/tracks`
- **Indexed Entity Directory**: Browse all tracked persons with lifespan windows, average confidence scores, and alert indicators.
- **Forensic Dossier Pane**: First detected and last detected timestamps, total lifespan duration (`49s`), and average confidence (`94%`).
- **Sequential Behaviour Timeline**: Chronological action sequences with exact durations (`Walking` 17s → `Approaching Restricted Area` 10s → `Restricted Area Entry` 13s) and anomaly phase highlighting.
- **Spatial Trajectory Coordinates**: Direct tabular view of spatial bounding box waypoints over time (`models/TrackPosition`).

---

### 3. System Analytics & Anomaly Forensics
High-level statistical analysis, risk classification breakdowns, and temporal trend visualization.

![Analytics Preview](screenshots/Screenshot%202026-10-07%20162759.png)

- **Route**: `/analytics`
- **Temporal Activity & Breach Frequency Chart**: Dual-curve area visualization showing total entities ingested (cyan) against flagged security breaches (rose) over 30-second intervals.
- **Risk Tier Breakdown Donut Chart**: Proportional distribution of incident severity levels (`HIGH RISK`, `MEDIUM RISK`, `LOW RISK`).

---

### 4. System Settings & Multi-Laptop Gateway Control
Operational threshold sliders, architecture matrix, and seamless multi-laptop networking configuration for hackathon presentations.

![Settings Preview](screenshots/Screenshot%202026-10-07%20162810.png)

- **Route**: `/settings`
- **Algorithm Threshold Controls**: Sliders for YOLOv8 detection confidence (`0.65`), temporal behaviour sensitivity (`0.75`), and alert escalation (`0.80`).
- **Multi-Laptop Network Manager**:
  - Direct IP configuration input for Member 3's backend (`http://<LAN_IP>:8000`).
  - One-click presets (`localhost:8000`, `Wi-Fi LAN IP`, `ngrok Tunnel`).
  - Real-time round-trip latency ping test against the FastAPI `/health` endpoint.
  - One-click switch between **Standalone Mock Engine** (fail-safe offline demo) and **Live FastAPI Backend**.
  - Direct link to FastAPI Swagger Documentation (`/docs`).
- **Team Integration Status**: Visual matrix displaying contract synchronization across all 4 teammates.

---

### 5. Video Intelligence Workspace & Forensic Dossiers
- **Video Analysis (`/analysis`)**:
  - Live video playback synchronized with real-time bounding box annotations.
  - Interactive safety zone polygons with dynamic breach alerts (`Restricted Hazardous Enclosure`, `Outer Perimeter Caution Buffer`).
  - HUD overlay toggles (`ZONES: ON/OFF`, `HUD: ON/OFF`), seekable video timeline with event markers, and active entity panel.
  - Toolbar buttons to trigger simulated ingestion of Member 1 tracks (`+ Tracks (M1)`) and Member 2 behaviours (`+ Behaviours (M2)`).
- **Incident Evidence Modal (`/events`)**:
  - Dual-mode forensic evidence inspection: toggle between photographic keyframe snapshots (`storage/evidence/`) and recorded `.mp4` video clips (`storage/event_clips/`).

---

## 🤝 4-Person Team Integration Summary

| Team Member | Subsystem Role | Tech Stack | Primary API Endpoint / Contract |
| :--- | :--- | :--- | :--- |
| **Member 1** | Object Detection & Tracking | Python, YOLO11n, ByteTrack, OpenCV | `POST /api/videos/{video_id}/tracks/import` |
| **Member 2** | Behaviour Intelligence & Posture/Fall Reasoning | Python, NumPy, Kinematic State Machine | `POST /api/videos/{video_id}/behaviours/import` |
| **Member 3** | Backend, PostgreSQL & Event Engine | FastAPI, PostgreSQL 15, SQLAlchemy, Docker | Central REST Gateway (`http://<LAN_IP>:8000/api`) |
| **Member 4** | Interactive Frontend Dashboard & UI Integration | React 19, TypeScript, Vite, Tailwind CSS, Recharts | Consumer of all REST APIs & WebSocket streams |

---

## ⚡ Quickstart Guide

### 1. Run Frontend Application (Member 4)
```bash
# Clone the repository
git clone -b ui https://github.com/somenparida/999ms.git
cd 999ms

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open **`http://localhost:5173/`** in your browser.

### 2. Run Backend Server (Member 3)
```bash
cd backend

# Option A: Start with automatic IP detection
./start_server.sh

# Option B: Start with Docker Compose (PostgreSQL 15 + FastAPI)
docker compose up --build
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Health Check Endpoint: `http://localhost:8000/health`

### 3. Connect Across Multiple Laptops Over Wi-Fi / Hotspot
1. Ensure both laptops are connected to the same Wi-Fi network or phone hotspot.
2. Note Member 3's local IP address (e.g., `192.168.1.50` or `10.89.105.218`).
3. In the AUTOVISION frontend, navigate to **Settings** (`/settings`):
   - In **Target Backend IP / Base URL**, enter: `http://<MEMBER_3_IP>:8000`
   - Click **Save URL**.
   - Click **Test Connection / Ping** to verify connectivity and latency.
   - Click **Switch to Live API** to begin streaming live backend data.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, TypeScript, Vite 6, Tailwind CSS v4, Lucide Icons, Recharts, Axios, React Router v7.
- **Backend**: FastAPI, Python 3.11, PostgreSQL 15, SQLAlchemy 2.0, Alembic, Pydantic v2, Docker Compose.
- **Computer Vision & AI**: Ultralytics YOLO11n, ByteTrack, OpenCV, NumPy, COCO 17-Keypoint Kinematics.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
