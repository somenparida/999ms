# Member 3 — Backend, PostgreSQL & Integration Layer

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

This document is the implementation instruction for Member 3.

The goal is to build the complete backend and integration layer that connects all four team members into one working system.

## 1. Role

Member 1: Object Detection + Object Tracking

Member 2: Behaviour Analysis + Anomaly Detection

Member 4: Frontend Dashboard + Visualization

Member 3 owns:

- PostgreSQL
- FastAPI
- SQLAlchemy
- Alembic
- Data contracts
- Event management
- Evidence management
- Analysis jobs
- Integration APIs
- Testing
- Docker

## 2. Main Objective

Build a backend that acts as the single source of truth for the complete application.

```text
Member 1
   ↓
Track Data
   ↓
Member 3
   ↓
PostgreSQL
   ↓
Member 2
   ↓
Behaviour Data
   ↓
Member 3
   ↓
Events + Evidence
   ↓
Member 4
   ↓
Dashboard
```

The backend must not depend on the internal implementation of Members 1 or 2.

## 3. Technology Stack

Use:

- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn
- python-multipart
- pytest
- httpx
- python-dotenv

Optional:

- Docker
- Docker Compose

## 4. Database

Use PostgreSQL as the primary persistent database.

The main entities are:

```text
Video
 ↓
Track
 ↓
Track Position
 ↓
Behaviour
 ↓
Event
 ↓
Evidence
```

Do not store actual video files inside PostgreSQL. Store files on disk/object storage and paths or URLs in PostgreSQL.

## 5. Required Tables

Implement:

- `videos`
- `tracks`
- `track_positions`
- `behaviours`
- `events`
- `evidence`
- `analysis_jobs`
- `zones`

## 6. Videos

Fields:

```text
id
filename
original_filename
file_path
duration
fps
width
height
total_frames
status
created_at
updated_at
```

Status:

```text
uploaded
queued
processing
completed
failed
```

## 7. Tracks

Fields:

```text
id
video_id
track_id
object_type
start_time
end_time
first_seen_frame
last_seen_frame
average_confidence
metadata
created_at
```

## 8. Track Positions

Fields:

```text
id
track_id
timestamp
frame_number
x
y
width
height
center_x
center_y
confidence
velocity
metadata
```

Example:

```json
{
  "track_id": 7,
  "timestamp": 42.31,
  "frame_number": 1269,
  "bbox": [120,80,220,350],
  "center": [170,215],
  "confidence": 0.94
}
```

## 9. Behaviours

Fields:

```text
id
video_id
track_id
behaviour_type
start_time
end_time
confidence
classification
reason
metadata
created_at
```

Possible types:

```text
walking
standing
stationary
running
restricted_area_entry
prolonged_inactivity
possible_fall
```

Do not hard-code the database to only these values.

## 10. Events

Fields:

```text
id
video_id
track_id
behaviour_id
event_type
severity
start_time
end_time
confidence
reason
status
metadata
created_at
```

Severity:

```text
low
medium
high
critical
```

Status:

```text
detected
reviewed
confirmed
dismissed
```

Every meaningful abnormal behaviour should be capable of becoming an event.

## 11. Evidence

Fields:

```text
id
event_id
evidence_type
file_path
timestamp
frame_number
description
metadata
created_at
```

Types:

```text
frame
image
video_clip
trajectory
bounding_box
```

## 12. Analysis Jobs

Fields:

```text
id
video_id
status
progress
current_stage
started_at
completed_at
error_message
metadata
```

Stages:

```text
queued
video_processing
detection
tracking
behaviour_analysis
event_generation
completed
failed
```

## 13. Zones

Fields:

```text
id
video_id
name
zone_type
coordinates
enabled
metadata
```

Store polygon coordinates as JSONB if appropriate.

## 14. Project Structure

Create:

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── videos.py
│   │   ├── tracks.py
│   │   ├── behaviours.py
│   │   ├── events.py
│   │   ├── evidence.py
│   │   ├── analysis.py
│   │   ├── zones.py
│   │   └── health.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── db/
│   ├── core/
│   └── utils/
├── migrations/
├── tests/
├── mock/
│   ├── tracks.json
│   ├── behaviours.json
│   └── events.json
├── storage/
│   ├── videos/
│   ├── processed/
│   ├── evidence/
│   └── event_clips/
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 15. API Endpoints

Implement:

```http
POST /api/videos/upload
GET /api/videos
GET /api/videos/{video_id}
DELETE /api/videos/{video_id}

POST /api/videos/{video_id}/analyze
GET /api/videos/{video_id}/analysis
POST /api/videos/{video_id}/analysis/cancel

POST /api/videos/{video_id}/tracks/import
GET /api/videos/{video_id}/tracks
GET /api/videos/{video_id}/tracks/{track_id}
GET /api/videos/{video_id}/tracks/{track_id}/positions

POST /api/videos/{video_id}/behaviours/import
GET /api/videos/{video_id}/behaviours

GET /api/videos/{video_id}/events
GET /api/events/{event_id}
PATCH /api/events/{event_id}

GET /api/events/{event_id}/evidence

GET /api/videos/{video_id}/timeline
GET /api/videos/{video_id}/summary

GET /health
```

## 16. Member 1 Integration

Support:

```http
POST /api/videos/{video_id}/tracks/import
```

Input:

```json
{
  "tracks": [
    {
      "track_id": 7,
      "object_type": "person",
      "timestamp": 42.31,
      "frame_number": 1269,
      "bbox": [120,80,220,350],
      "center": [170,215],
      "confidence": 0.94
    }
  ]
}
```

Validate and store the data without caring how Member 1 generated it.

## 17. Member 2 Integration

Support:

```http
POST /api/videos/{video_id}/behaviours/import
```

Input:

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
      "reason": "Person entered restricted zone."
    }
  ]
}
```

Validate the video and track, store the behaviour, and generate an event when appropriate.

## 18. Event Generation

Conceptually:

```text
Behaviour
    ↓
classification == abnormal
    ↓
Event Service
    ↓
Event
    ↓
Evidence
```

Avoid duplicate events when the same behaviour is imported multiple times.

## 19. Timeline

`GET /api/videos/{video_id}/timeline` should return chronological behaviours/events, for example:

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
    "classification": "abnormal"
  }
]
```

## 20. Dashboard Summary

`GET /api/videos/{video_id}/summary` should return:

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

## 21. Environment

Create `.env.example`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/vision_behaviour

UPLOAD_DIR=./storage/videos
OUTPUT_DIR=./storage/processed
EVIDENCE_DIR=./storage/evidence

CORS_ORIGINS=http://localhost:3000

DEBUG=true
```

Never commit real credentials.

## 22. Docker

Create:

```text
Dockerfile
docker-compose.yml
```

At minimum provide:

```text
backend
postgres
```

The goal is:

```bash
docker compose up
```

## 23. Mock Data

Create realistic:

```text
mock/tracks.json
mock/behaviours.json
mock/events.json
```

The backend must work before Members 1 and 2 finish.

## 24. Testing

Use pytest.

Test:

- Database operations
- API endpoints
- Validation
- Track import
- Behaviour import
- Event generation
- Evidence
- Timeline
- Summary
- Full integration flow

At least one integration test must prove:

```text
Track Data
 ↓
Behaviour Data
 ↓
Event
 ↓
Evidence
 ↓
API Retrieval
```

## 25. Idempotency

Avoid uncontrolled duplicate track positions and duplicate events when identical data is submitted more than once.

Use sensible uniqueness constraints or deduplication logic.

## 26. Error Handling

Use:

```text
400 Bad Request
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

Return structured errors.

## 27. Logging

Log:

- Video upload
- Analysis start
- Analysis completion
- Track import
- Behaviour import
- Event creation
- Evidence creation
- Database errors
- API errors

## 28. FastAPI Documentation

Ensure:

```text
/docs
```

works and every endpoint has useful descriptions and schemas.

## 29. Implementation Order

Follow:

1. Create project structure.
2. Configure PostgreSQL.
3. Create SQLAlchemy models.
4. Create Alembic migrations.
5. Run database.
6. Create Pydantic schemas.
7. Create services.
8. Create video APIs.
9. Create track APIs.
10. Create behaviour APIs.
11. Create event engine.
12. Create evidence APIs.
13. Create analysis APIs.
14. Create timeline and summary APIs.
15. Create mock data.
16. Create tests.
17. Add Docker.
18. Integrate Member 1.
19. Integrate Member 2.
20. Integrate Member 4.
21. Run complete end-to-end test.

## 30. Final End-to-End Test

The following must work:

```text
Upload Video
      ↓
Create Video Record
      ↓
Start Analysis Job
      ↓
Member 1 Produces Tracks
      ↓
Track Data Imported
      ↓
Member 2 Produces Behaviours
      ↓
Behaviour Data Imported
      ↓
Abnormal Behaviour Detected
      ↓
Event Created
      ↓
Evidence Attached
      ↓
PostgreSQL Stores Results
      ↓
Member 4 Requests API
      ↓
Dashboard Displays Result
```

## 31. Completion Criteria

Do not consider the task complete until:

- PostgreSQL works
- Database schema works
- Alembic works
- FastAPI starts
- `/health` works
- `/docs` works
- Video upload works
- Track import works
- Track retrieval works
- Behaviour import works
- Event generation works
- Evidence management works
- Analysis status works
- Timeline works
- Summary works
- Mock data works
- Member 1 data integrates
- Member 2 data integrates
- Member 4 can consume APIs
- Duplicate data is handled
- Validation works
- Tests pass
- Docker works
- Documentation is complete

The backend is the stable integration backbone of the entire HackNex project.
