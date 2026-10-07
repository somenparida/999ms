# Autonomous Vision & Behaviour Intelligence — Backend Engine

![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?style=for-the-badge&logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00.svg?style=for-the-badge&logo=sqlite)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=for-the-badge&logo=docker)
![Pytest](https://img.shields.io/badge/Pytest-9--Passed-46A2F1.svg?style=for-the-badge&logo=pytest)
![License](https://img.shields.io/badge/HackNex-2026--HNX26PSI07-orange.svg?style=for-the-badge)

**Subsystem**: Member 3 — Backend, PostgreSQL & Integration Subsystem  
**Project**: HNX26PSI07 — Autonomous Vision & Behaviour Understanding  
**Event**: HackNex 2026  

---

## 📌 Executive Summary & System Overview

The **Backend & Integration Subsystem (Member 3)** serves as the central nerve center and data orchestration layer for the **Autonomous Vision & Behaviour Understanding System**. It unifies machine-learning perception models (Member 1), posture and anomaly reasoning models (Member 2), and real-time visualization dashboards (Member 4) into a cohesive, high-throughput, microservice architecture.

### Primary Objectives & Capabilities
1. **Decoupled Integration Architecture**: Provides high-performance RESTful APIs connecting 4 separate laptops operating over a shared Mobile Hotspot or Local Area Network (LAN).
2. **Flexible Track Ingestion Engine**: Consumes object tracking payloads from **Member 1** (YOLOv8/11 + ByteTrack), featuring automated coordinate discrimination for both $[x_1, y_1, x_2, y_2]$ absolute bounding boxes and $[x, y, w, h]$ dimensions, alongside 17 COCO pose keypoints.
3. **Behavioral Anomaly Ingestion**: Parses spatial-temporal activity predictions from **Member 2** (`STANDING`, `WALKING`, `RUNNING`, `SITTING`, `CROUCHING`, `BENDING`, `LYING`, `FALLING`, `UNKNOWN`) and normality ratings (`NORMAL`, `POTENTIALLY_UNUSUAL`, `ABNORMAL`).
4. **Automated Event Generation Engine**: Auto-evaluates behavior data against security rules and restricted zone geofences, raising prioritized security events (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) with deduplication checks.
5. **3-Tier Explainable Evidence Generation**: Instantly extracts and formats evidence packages for security personnel, including:
   - **Bounding Box Artifacts**: Position snapshot $[x, y, w, h]$ with confidence scores.
   - **Historical Trajectory Paths**: 2D coordinate movement history over time.
   - **Biomechanical Pose Skeletons**: 17 COCO keypoints `[[x, y, confidence], ...]`.
6. **Dashboard KPI & Timeline Aggregation Engine**: Serves 7 real-time KPI metrics and paginated chronological feeds for **Member 4's** interactive React/Next.js dashboard.
7. **Dual-Database Compatibility**: Supports zero-config **SQLite** (`vision_behaviour.db`) for immediate local development and **PostgreSQL 15** (via Docker Compose & Alembic migrations) for production deployment.

---

## 🗺️ Subsystem Architecture & Multi-Laptop Topology

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              MEMBER 1: OBJECT DETECTION & TRACKING                     │
│                              (YOLOv8/11 + ByteTrack + Pose Estimator)                  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            │ POST /api/videos/{id}/tracks/import
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              MEMBER 3: BACKEND ENGINE & DATABASE                       │
│                              (FastAPI + PostgreSQL / SQLite ORM Layer)                 │
│                                                                                        │
│   ┌───────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────┐   │
│   │ Automated Event Generation│   │ Explainable Evidence Engine│   │ Geofence Engine │   │
│   │ (Alerts & Deduplication)  │   │ (BBox, Trajectory, Pose) │   │ (Restricted Zone│   │
│   └───────────────────────────┘   └──────────────────────────┘   └─────────────────┘   │
└──────────────────────┬────────────────────────────────────────────┬────────────────────┘
                       │                                            │
                       │ POST /api/videos/{id}/behaviours/import    │ GET /api/videos/{id}/summary
                       ▼                                            ▼
┌──────────────────────────────────────────────┐   ┌─────────────────────────────────────┐
│ MEMBER 2: BEHAVIOUR INTELLIGENCE             │   │ MEMBER 4: FRONTEND DASHBOARD UI     │
│ (Posture Classification & Fall Detection)    │   │ (React Canvas Overlay & Evidence)   │
└──────────────────────────────────────────────┘   └─────────────────────────────────────┘
```

---

## ⚡ Key Architectural Features & Breakthroughs

### 1. Robust Bounding Box Coordinate Discrimination
Member 1 implementations vary between absolute corner coordinates $[x_1, y_1, x_2, y_2]$ and offset dimension coordinates $[x, y, w, h]$. The backend automatically detects the format:
$$\text{If } bbox[2] > bbox[0] \text{ and } bbox[3] > bbox[1] \implies [x_1, y_1, x_2, y_2] \rightarrow \text{Converted to } [x, y, w - x, h - y]$$
This guarantees seamless visualization regardless of detector output structure.

### 2. Pydantic V2 Flexible Schema Aliasing
The schema layer (`app/schemas/`) utilizes Pydantic `AliasChoices` to resolve variable naming discrepancies between ML models and database contracts:
- `activity` $\leftrightarrow$ `behaviour_type`
- `status` $\leftrightarrow$ `classification`
- `timestamp` $\leftrightarrow$ `start_time`

### 3. Automated Event Generation & Deduplication
When Member 2 pushes behavior imports or when track updates violate zone boundaries:
- Security events are instantiated automatically for anomalous activities (`FALLING`, `LYING`, `ABNORMAL`, or restricted zone intrusions).
- Severity level is determined dynamically (`restricted_area_entry` $\rightarrow$ `HIGH`, `possible_fall` $\rightarrow$ `CRITICAL`).
- Duplicate alerts for the same track within a 5-second temporal window are automatically suppressed.

### 4. Zero-Config Local Hotspot Startup
The included startup utility `start_server.sh` automatically probes active network interfaces (`wlo1`, `eth0`, `en0`), identifies the host's Local IP address (e.g., `10.89.105.218`), updates CORS configuration, and launches Uvicorn on `0.0.0.0:8000`.

---

## 📂 Project Directory Structure

```text
backend/
├── app/
│   ├── api/                    # REST API Routers
│   │   ├── analysis.py         # Video analysis job management & progress polling
│   │   ├── behaviours.py       # Member 2 behaviour ingestion & query endpoints
│   │   ├── events.py           # Security event alert endpoints & status management
│   │   ├── evidence.py         # Explainable evidence extraction (BBox, Trajectory, Pose)
│   │   ├── health.py           # Server readiness & database health probes
│   │   ├── tracks.py           # Member 1 track import & position time-series
│   │   ├── videos.py           # Video file upload & metadata management
│   │   └── zones.py            # Restricted area polygon geofence management
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (.env configuration)
│   │   └── logging.py          # Structured log formatting
│   ├── db/
│   │   ├── base.py             # Declarative base & metadata registration
│   │   └── session.py          # SQLAlchemy engine & session maker
│   ├── models/                 # SQLAlchemy 2.0 ORM Models
│   │   ├── analysis_job.py     # Asynchronous video analysis job tracking
│   │   ├── behaviour.py        # Classified activity & posture predictions
│   │   ├── event.py            # Security alerts & review status
│   │   ├── evidence.py         # Associated explainability artifacts
│   │   ├── track.py            # Tracked entity metadata
│   │   ├── track_position.py   # Spatiotemporal coordinate time-series & keypoints
│   │   ├── video.py            # Video metadata & frame dimensions
│   │   └── zone.py             # Geofence polygon vertices & alert rules
│   ├── schemas/                # Pydantic Input/Output Validation Contracts
│   │   ├── analysis_job.py
│   │   ├── behaviour.py
│   │   ├── event.py
│   │   ├── evidence.py
│   │   ├── track.py
│   │   ├── video.py
│   │   └── zone.py
│   ├── services/               # Core Business Logic & Event Engine
│   │   ├── analysis_service.py # Job execution & stage tracking
│   │   ├── behaviour_service.py# Ingestion & event triggering logic
│   │   ├── event_service.py    # Event CRUD & status updates
│   │   ├── evidence_service.py # Evidence extraction & artifact assembly
│   │   ├── summary_service.py  # Dashboard 7-KPI aggregation & timeline feed
│   │   ├── track_service.py    # Track & position persistence logic
│   │   ├── video_service.py    # Video processing & metadata retrieval
│   │   └── zone_service.py     # Polygon point-in-polygon spatial detection
│   └── main.py                 # FastAPI Application Factory & Middleware Setup
├── migrations/                 # Alembic Database Migration Scripts
├── mock/                       # Real-world verification datasets (tracks.json)
├── storage/                    # Disk Storage (videos, processed, evidence)
├── tests/                      # Automated Test Suite (9 Pytest modules)
│   ├── test_analysis.py
│   ├── test_behaviours.py
│   ├── test_events.py
│   ├── test_evidence.py
│   ├── test_health.py
│   ├── test_integration.py     # End-to-End full pipeline integration test
│   ├── test_tracks.py          # Real-world tracks.json import test
│   ├── test_videos.py
│   └── test_zones.py
├── .env.example                # Template for environment variables
├── Dockerfile                  # Container build specification
├── docker-compose.yml          # PostgreSQL 15 + FastAPI orchestrator
├── MEMBER_4_FRONTEND_PROMPT.md # AI Generation Prompt for Member 4 UI
├── requirements.txt            # Python dependency definitions
└── start_server.sh             # Auto-IP network startup script
```

---

## 🗄️ Database Schema & Entity-Relationship Architecture

The system uses 8 relational tables designed to handle high-frequency spatial-temporal tracking streams while maintaining strict data integrity:

```text
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│     videos      │1     * │     tracks      │1     * │ track_positions │
├─────────────────┤────────┼─────────────────┤────────┼─────────────────┤
│ id (PK)         │        │ id (PK)         │        │ id (PK)         │
│ filename        │        │ video_id (FK)   │        │ track_id (FK)   │
│ duration        │        │ track_number    │        │ frame_number    │
│ fps, width      │        │ label           │        │ timestamp       │
└────────┬────────┘        └────────┬────────┘        │ bbox [x,y,w,h]  │
         │                          │                 │ pose_keypoints  │
         │1                         │1                └─────────────────┘
         │                          │
         │*                         │*
┌────────┴────────┐        ┌────────┴────────┐        ┌─────────────────┐
│  analysis_jobs  │        │   behaviours    │1     * │     events      │
├─────────────────┤        ├─────────────────┤────────┼─────────────────┤
│ id (PK)         │        │ id (PK)         │        │ id (PK)         │
│ video_id (FK)   │        │ track_id (FK)   │        │ video_id (FK)   │
│ status, progress│        │ behaviour_type  │        │ track_id (FK)   │
└─────────────────┘        │ classification  │        │ event_type      │
                           └─────────────────┘        │ severity, status│
                                                      └────────┬────────┘
                                                               │1
                                                               │*
                                                      ┌────────┴────────┐
                                                      │    evidences    │
                                                      ├─────────────────┤
                                                      │ id (PK)         │
                                                      │ event_id (FK)   │
                                                      │ evidence_type   │
                                                      │ payload (JSON)  │
                                                      └─────────────────┘
```

---

## 🚀 Quickstart & Server Launch

### Prerequisite Checklist
- Python 3.10+ installed
- Virtual environment activated (`python3 -m venv venv && source venv/bin/activate`)
- Dependencies installed (`pip install -r requirements.txt`)

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Launch Development Server (Auto-IP Hotspot Mode)
Execute the multi-laptop auto-detection startup script:
```bash
cd backend
chmod +x start_server.sh
./start_server.sh
```
*The script automatically resolves your local network IP (e.g., `10.89.105.218`) and binds Uvicorn to `0.0.0.0:8000`.*

### 3. Launch via Direct Python Command
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Interactive API Documentation & Health Check
- **OpenAPI Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Spec**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **System Health Probe**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🐳 Docker Production Deployment (PostgreSQL 15)

To run the complete production stack including **PostgreSQL 15** and **FastAPI**:

```bash
cd backend
docker compose up --build -d
```

### Environment Variables for PostgreSQL (`docker-compose.yml`)
```yaml
POSTGRES_USER: vision_user
POSTGRES_PASSWORD: vision_password
POSTGRES_DB: vision_behaviour_db
DATABASE_URL: postgresql://vision_user:vision_password@db:5432/vision_behaviour_db
```

### Apply Database Migrations (Alembic)
```bash
docker compose exec backend alembic upgrade head
```

---

## 📡 API Contract Reference

### 1. Videos & Analysis Jobs Router (`/api/videos`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/videos/upload` | Upload video file (`.mp4`, `.avi`, `.mov`) |
| `GET` | `/api/videos` | List all uploaded video records |
| `GET` | `/api/videos/{video_id}` | Fetch video metadata & processing status |
| `DELETE`| `/api/videos/{video_id}` | Delete video and all associated DB records |
| `POST` | `/api/videos/{video_id}/analyze` | Trigger background analysis pipeline |
| `GET` | `/api/videos/{video_id}/analysis` | Poll job execution stage & progress percentage |

#### Video Upload Response Example:
```json
{
  "id": 1,
  "filename": "multi_person1.mp4",
  "filepath": "storage/videos/multi_person1.mp4",
  "fps": 30.0,
  "width": 1920,
  "height": 1080,
  "total_frames": 900,
  "duration": 30.0,
  "status": "uploaded"
}
```

---

### 2. Member 1: Track Import Router (`/api/videos/{id}/tracks`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/videos/{video_id}/tracks/import` | Bulk import track coordinate streams & keypoints |
| `GET` | `/api/videos/{video_id}/tracks` | List all unique tracked entities in video |
| `GET` | `/api/videos/{video_id}/tracks/{track_id}/positions` | Fetch complete coordinate time-series for track |

#### Track Import Payload (`POST /api/videos/1/tracks/import`):
```json
{
  "tracks": [
    {
      "track_id": 1,
      "label": "person",
      "positions": [
        {
          "frame_number": 0,
          "timestamp": 0.0,
          "bbox": [450, 200, 120, 310],
          "confidence": 0.94,
          "pose_keypoints": [
            [480, 210, 0.95],
            [485, 205, 0.92]
          ]
        }
      ]
    }
  ]
}
```

---

### 3. Member 2: Behaviour Import Router (`/api/videos/{id}/behaviours`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/videos/{video_id}/behaviours/import` | Bulk import posture classifications & trigger Event Engine |
| `GET` | `/api/videos/{video_id}/behaviours` | List all recorded behavior classifications |

#### Behaviour Import Payload (`POST /api/videos/1/behaviours/import`):
```json
{
  "behaviours": [
    {
      "track_id": 1,
      "behaviour_type": "FALLING",
      "classification": "ABNORMAL",
      "confidence": 0.96,
      "start_time": 4.5,
      "end_time": 6.2,
      "severity": "CRITICAL",
      "metadata": {
        "posture_change_velocity": 2.4,
        "impact_detected": true
      }
    }
  ]
}
```

---

### 4. Security Events & Alert Management Router (`/api/events`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/videos/{video_id}/events` | Fetch all detected anomaly events for video |
| `GET` | `/api/events/{event_id}` | Fetch detailed event record |
| `PATCH`| `/api/events/{event_id}` | Update review status (`reviewed`, `confirmed`, `dismissed`) |

#### Event Schema Response:
```json
{
  "id": 1,
  "video_id": 1,
  "track_id": 1,
  "event_type": "possible_fall",
  "severity": "CRITICAL",
  "status": "detected",
  "start_time": 4.5,
  "end_time": 6.2,
  "description": "Critical anomaly: Person #1 exhibited FALLING posture.",
  "created_at": "2026-10-07T16:30:00Z"
}
```

---

### 5. Explainable Evidence Extraction Router (`/api/events/{id}/evidence`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/events/{event_id}/evidence` | Fetch 3-pillar explainability package for security audit |

#### Evidence Package Response Example:
```json
{
  "event_id": 1,
  "evidences": [
    {
      "evidence_type": "bounding_box",
      "payload": {
        "track_id": 1,
        "frame_number": 135,
        "bbox": [450, 200, 120, 310],
        "confidence": 0.96
      }
    },
    {
      "evidence_type": "trajectory",
      "payload": {
        "track_id": 1,
        "points": [
          {"timestamp": 4.0, "x": 450, "y": 200},
          {"timestamp": 4.5, "x": 480, "y": 350}
        ]
      }
    },
    {
      "evidence_type": "pose_keypoints",
      "payload": {
        "track_id": 1,
        "keypoints": [[480, 210, 0.95], [485, 205, 0.92]]
      }
    }
  ]
}
```

---

### 6. Member 4: Dashboard Visualization Router (`/api/videos/{id}`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/videos/{video_id}/summary` | Fetch 7 aggregated real-time KPI metrics |
| `GET` | `/api/videos/{video_id}/timeline` | Fetch chronological timestamped activity feed |

#### Dashboard Summary KPI Payload (`GET /api/videos/1/summary`):
```json
{
  "video_id": 1,
  "people_detected": 4,
  "unique_tracks": 32,
  "normal_events": 28,
  "abnormal_events": 4,
  "high_risk_events": 2,
  "average_confidence": 0.942,
  "duration": 30.0
}
```

---

### 7. Restricted Zone Geofencing Router (`/api/zones`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/zones` | Create restricted area polygon |
| `GET` | `/api/videos/{video_id}/zones` | Fetch configured zone polygons for video |

#### Create Zone Payload:
```json
{
  "video_id": 1,
  "name": "Hazardous Machinery Zone A",
  "polygon_vertices": [
    {"x": 100, "y": 100},
    {"x": 500, "y": 100},
    {"x": 500, "y": 500},
    {"x": 100, "y": 500}
  ],
  "is_restricted": true
}
```

---

## 📱 Multi-Laptop Mobile Hotspot Networking Guide

When working in hackathon environments with 4 laptops connected to a single **Mobile Hotspot**:

### Host Server IP Identification
Your active Mobile Hotspot IP is: `10.89.105.218` (Port: `8000`).

```text
Member 1 (Laptop 1) ──> http://10.89.105.218:8000/api/videos/1/tracks/import
Member 2 (Laptop 2) ──> http://10.89.105.218:8000/api/videos/1/behaviours/import
Member 4 (Laptop 4) ──> http://10.89.105.218:8000/api/videos/1/summary
```

### Team Integration Cheat Sheet

```python
# Member 1 Track Import Snippet (Python)
import requests

url = "http://10.89.105.218:8000/api/videos/1/tracks/import"
payload = {
    "tracks": [
        {
            "track_id": 1,
            "label": "person",
            "positions": [
                {"frame_number": 0, "timestamp": 0.0, "bbox": [100, 150, 80, 200], "confidence": 0.92}
            ]
        }
    ]
}
response = requests.post(url, json=payload)
print(response.json())
```

```python
# Member 2 Behaviour Import Snippet (Python)
import requests

url = "http://10.89.105.218:8000/api/videos/1/behaviours/import"
payload = {
    "behaviours": [
        {
            "track_id": 1,
            "behaviour_type": "FALLING",
            "classification": "ABNORMAL",
            "confidence": 0.95,
            "start_time": 4.5,
            "end_time": 6.0
        }
    ]
}
response = requests.post(url, json=payload)
print(response.json())
```

*For step-by-step troubleshooting, firewall adjustments, and ngrok tunneling alternatives, refer to [`README_MULTI_LAPTOP_CONNECT.md`](file:///home/frost/hacknex/README_MULTI_LAPTOP_CONNECT.md).*

---

## 🧪 Automated Testing & Verification Suite

The backend includes a comprehensive `pytest` test suite with 9 modular test specifications:

```bash
cd backend
pytest -v
```

### Test Suite Summary
1. `test_health.py`: Validates database connectivity and service readiness probes.
2. `test_videos.py`: Tests video file upload, format validation, and metadata extraction.
3. `test_tracks.py`: Verifies track coordinate ingestion and real-world `tracks.json` dataset (849 positions, 32 tracks).
4. `test_behaviours.py`: Validates posture classification imports and state handling.
5. `test_events.py`: Verifies auto-event creation, severity assignment, and review status workflow.
6. `test_evidence.py`: Tests extraction of bounding box, 2D trajectory, and 17 COCO pose keypoints evidence.
7. `test_zones.py`: Validates spatial polygon creation and point-in-polygon geofence violation logic.
8. `test_analysis.py`: Verifies asynchronous job status polling and stage transitions.
9. `test_integration.py`: End-to-End full pipeline validation test:
   $$\text{Video Upload} \rightarrow \text{Track Ingestion} \rightarrow \text{Behaviour Ingestion} \rightarrow \text{Event Triggering} \rightarrow \text{Evidence Generation} \rightarrow \text{Dashboard Summary Retrieval}$$

---

## 🎨 Member 4 Frontend AI Generation Prompt

To assist Member 4 in constructing the dynamic React / Next.js visualization dashboard, refer to:
- Prompt Template: [`backend/MEMBER_4_FRONTEND_PROMPT.md`](file:///home/frost/hacknex/backend/MEMBER_4_FRONTEND_PROMPT.md)
- UI Specification: [`README_MEMBER_4_FRONTEND.md`](file:///home/frost/hacknex/README_MEMBER_4_FRONTEND.md)

---

## 📜 License & Acknowledgments

Developed for **HackNex 2026 — Track HNX26PSI07**  
*Autonomous Vision & Behaviour Understanding System*  

- **FastAPI**: Modern high-performance Python Web Framework
- **PostgreSQL / SQLAlchemy**: Enterprise Relational Data Store & ORM
- **YOLOv8/11 & ByteTrack**: Vision Tracking Foundation
- **COCO Pose standard**: 17 Keypoint Biomechanical Skeleton Model
