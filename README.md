# AUTOVISION — Autonomous Vision & Behaviour Understanding

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![React](https://img.shields.io/badge/React-19.0-61dafb.svg?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178c6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646cff.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38b2ac.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![FastAPI Ready](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

> **HackNex 2026 Hackathon** — Problem Statement **HNX26PSI07**  
> Central Frontend UI, Dashboard Telemetry, Video Intelligence Workspace & System Integration Subsystem.

---

## 📸 Application Showcase

### 1. Security & Behavioral Telemetry Dashboard
Real-time multi-agent vision intelligence, aggregate KPIs, active surveillance feed status, anomaly classification queue, and event distribution analytics.

![Dashboard Preview](screenshots/Screenshot%202026-10-07%20162736.png)

---

### 2. Track Explorer & Entity Dossiers
DeepSORT entity lifecycle analysis, temporal behavior history, individual track lifespans, and sequential state transitions with anomaly phase tracking.

![Track Explorer Preview](screenshots/Screenshot%202026-10-07%20162748.png)

---

### 3. System Analytics & Behavior Forensics
Statistical aggregate metrics, dual-curve temporal anomaly rates (Total Entities vs. Flagged Breaches) over 30-second windows, and risk tier distribution profiling.

![Analytics Preview](screenshots/Screenshot%202026-10-07%20162759.png)

---

### 4. System Settings, Thresholds & Multi-Laptop Gateway
Computer vision confidence sliders, temporal behaviour sensitivity parameters, multi-laptop Wi-Fi LAN IP configuration (`README_MULTI_LAPTOP_CONNECT.md`), connection latency ping tests, and team contract architecture mapping.

![Settings Preview](screenshots/Screenshot%202026-10-07%20162810.png)

---

## 🏛️ System Architecture & Team Roles

```text
VIDEO STREAM
    │
    ▼
[MEMBER 1] OBJECT DETECTION & TRACKING
    │   • YOLOv8 Entity Detection
    │   • DeepSORT Trajectory Tracker
    │   • Output Contract: Track[]
    │   • API: POST /api/videos/{video_id}/tracks/import
    ▼
[MEMBER 2] BEHAVIOUR INTELLIGENCE
    │   • Spatio-Temporal Action Classification
    │   • State Transitions & Anomaly Recognition
    │   • Output Contract: Behaviour[]
    │   • API: POST /api/videos/{video_id}/behaviours/import
    ▼
[MEMBER 3] BACKEND & EVENT ENGINE
    │   • FastAPI + PostgreSQL + SQLAlchemy + Alembic
    │   • Safety Zone Rules & Breach Triggering
    │   • Evidence Storage (Keyframe Images & .mp4 Event Clips)
    │   • Output Contract: Event[], Zone[], EvidenceRecord[]
    │   • API Gateway: http://<LAN_IP>:8000/api
    ▼
[MEMBER 4] AUTOVISION FRONTEND APPLICATION (This Repository)
    │   • Command & Control Dashboard
    │   • Video Intelligence Workspace with HUD & Bounding Boxes
    │   • Interactive Safety Zone Overlays (Restricted, Caution, Safe)
    │   • Forensic Event Dossier Modal (Photo Keyframes & .mp4 Video Player)
    │   • Track Explorer & Trajectory Coordinates Table (TrackPosition)
    │   • System Analytics Charts (Area & Donut Visualizations)
    │   • Multi-Laptop Wi-Fi Gateway Manager with Health Check Ping
```

---

## 🚀 Key Features

- **Video Intelligence Workspace (`/analysis`)**:
  - Live video playback with real-time entity bounding box overlays.
  - Interactive safety zone polygons (`Restricted Hazardous Enclosure`, `Outer Perimeter Caution Buffer`).
  - HUD controls: `ZONES: ON/OFF`, `HUD: ON/OFF`, seek-synchronized timeline, and live alert panels.
  - Direct pipeline import triggers for Member 1 (`+ Tracks (M1)`) and Member 2 (`+ Behaviours (M2)`).
- **Forensic Event Dossiers (`/events`)**:
  - Filterable incident audit log with severity indicators (`HIGH`, `MEDIUM`, `LOW`).
  - Dual-mode incident evidence modal: toggle between high-res keyframe photos (`/storage/evidence/`) and recorded `.mp4` video clips (`/storage/event_clips/`).
- **DeepSORT Track Explorer (`/tracks`)**:
  - Entity search and selection with lifespan tracking and confidence scores.
  - Sequential behaviour timelines with anomaly phases.
  - Granular spatial trajectory coordinates table matching PostgreSQL `models/TrackPosition`.
- **System Analytics (`/analytics`)**:
  - Recharts-powered temporal breach activity area charts and risk tier classification donut diagrams.
- **Multi-Laptop Network Manager (`/settings`)**:
  - Dynamic backend IP / URL configuration input to connect across teammate laptops over local Wi-Fi or ngrok tunnels.
  - Real-time latency measurement and ping check against the FastAPI `/health` endpoint.
  - Fail-safe toggle between **Standalone Mock Engine** (for offline stage demos) and **Live FastAPI Backend**.

---

## ⚡ Getting Started

### 1. Prerequisites
- **Node.js** v18+ or v20+
- **npm** or **pnpm**

### 2. Installation
```bash
# Clone repository
git clone -b ui https://github.com/somenparida/999ms.git
cd 999ms

# Install dependencies
npm install
```

### 3. Start Development Server
```bash
npm run dev
```
The application will launch on **`http://localhost:5173/`**.

### 4. Build for Production
```bash
npm run build
```

---

## 🤝 Multi-Laptop Team Integration Guide

When connecting with teammates during the hackathon:
1. Ensure both laptops are on the same Wi-Fi network (or hotspot).
2. Member 3 starts the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. In the AUTOVISION UI, open **Settings** (`/settings`):
   - Enter Member 3's Wi-Fi IP: `http://192.168.x.x:8000`
   - Click **Save URL**.
   - Click **Test Connection / Ping** to verify connectivity and latency.
   - Switch the environment mode toggle to **Live FastAPI Backend**.

---

## 📄 License
Licensed under the [MIT License](LICENSE).
