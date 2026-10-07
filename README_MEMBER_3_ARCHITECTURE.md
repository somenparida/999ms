# Member 3 — Architecture, Features & Design Documentation

## HNX26PSI07 — Autonomous Vision & Behaviour Understanding

## 1. Overview

This module is the backend and integration backbone of the Autonomous Vision & Behaviour Understanding system.

The complete project combines:

- Computer vision
- Object detection
- Object tracking
- Behaviour analysis
- Temporal reasoning
- Anomaly detection
- Event generation
- Evidence management
- Data persistence
- Interactive visualization

Member 3 makes these independently developed components operate as one coherent system.

The backend receives structured outputs from the AI modules, stores them in PostgreSQL, converts abnormal behaviours into meaningful events, manages evidence, and exposes REST APIs to the frontend.

---

# 2. Why This Module Exists

Member 1 determines:

> What objects exist and where they are.

Member 2 determines:

> What those objects are doing and whether the behaviour is abnormal.

Member 4 presents:

> What the system discovered to the user.

Member 3 connects these parts.

```text
Detection
    ↓
Tracking
    ↓
Behaviour
    ↓
Event
    ↓
Evidence
    ↓
Database
    ↓
API
    ↓
Dashboard
```

---

# 3. Core Architecture

```text
                     VIDEO
                       │
                       ▼
              ┌─────────────────┐
              │     MEMBER 1    │
              │ Detection +     │
              │ Tracking        │
              └────────┬────────┘
                       │
                       │ Track Data
                       ▼
              ┌─────────────────┐
              │     MEMBER 2    │
              │ Behaviour       │
              │ Intelligence    │
              └────────┬────────┘
                       │
                       │ Behaviour Data
                       ▼
        ┌──────────────────────────────────┐
        │             MEMBER 3             │
        │                                  │
        │             FastAPI              │
        │                │                 │
        │        ┌───────┴───────┐         │
        │        │               │         │
        │   Event Engine    Evidence      │
        │        │               │         │
        │        └───────┬───────┘         │
        │                │                 │
        │           PostgreSQL             │
        └────────────────┬─────────────────┘
                         │
                         │ REST API
                         ▼
                ┌─────────────────┐
                │     MEMBER 4    │
                │    Dashboard    │
                └─────────────────┘
```

---

# 4. Main Features

The backend provides:

1. Video Management
2. PostgreSQL Data Storage
3. Track Storage
4. Temporal Track History
5. Behaviour Storage
6. Event Generation
7. Structured Events
8. Event Severity
9. Evidence Management
10. Analysis Job Tracking
11. Timeline
12. Dashboard Summary
13. REST API
14. Stable Data Contracts
15. Mock Data Integration
16. Testing
17. Docker Deployment

---

# 5. Video Management

The system allows users to upload and manage analysis videos.

Stored information includes:

```text
Filename
Duration
FPS
Resolution
Frame count
Processing status
File location
```

Every other analysis object belongs to a video.

```text
Video
 ├── Tracks
 ├── Behaviours
 ├── Events
 ├── Evidence
 └── Zones
```

---

# 6. PostgreSQL Data Storage

PostgreSQL is the central persistent database.

The system contains strongly related entities:

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

A relational database maintains these relationships and supports filtering, history, multiple videos, multiple tracks, events, and evidence.

JSON/JSONB is used for flexible metadata where appropriate.

---

# 7. Track Storage

Member 1 generates tracked entities such as:

```text
Person #1
Person #2
Person #7
```

The backend stores:

- Track ID
- Object type
- Start time
- End time
- Confidence
- Position
- Bounding box
- Frame number
- Velocity

This allows historical movement to be queried later.

---

# 8. Temporal Track History

A single detection cannot describe behaviour.

Example:

```text
Frame 1:
Person at X=100

Frame 2:
Person at X=105

Frame 3:
Person at X=110

Frame 4:
Person at X=110

Frame 5:
Person at X=110
```

The sequence indicates movement followed by inactivity.

The backend therefore stores track positions over time.

This supports:

- Trajectory visualization
- Movement analysis
- Duration calculations
- Behaviour analysis
- Evidence generation

---

# 9. Behaviour Storage

Member 2 analyzes tracked objects.

Example:

```text
Person #7
↓
Walking
↓
Restricted Area Entry
↓
Stationary
↓
Exit
```

Each behaviour stores:

```text
Type
Track ID
Start time
End time
Confidence
Classification
Reason
Metadata
```

---

# 10. Event Generation

Not every behaviour should become an alert.

For example:

```text
Walking
```

is generally normal.

But:

```text
Restricted Area Entry
```

may become a meaningful event.

Therefore the architecture separates:

```text
Behaviour
```

from:

```text
Event
```

A behaviour describes what happened.

An event represents something meaningful enough to report.

---

# 11. Structured Events

Every important event should answer:

```text
WHO?
WHAT?
WHEN?
HOW CONFIDENT?
WHY?
```

Example:

```text
WHO:
Person #7

WHAT:
Restricted Area Entry

WHEN:
00:42 – 00:55

CONFIDENCE:
94%

WHY:
Person #7 crossed the predefined restricted boundary.
```

This directly supports the problem requirement that unusual behaviour identify the entity and time.

---

# 12. Event Severity

Events can be classified:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Example:

```text
Normal walking
→ No event

Prolonged inactivity
→ Medium

Restricted area entry
→ High

Serious safety incident
→ Critical
```

Severity thresholds should remain configurable.

---

# 13. Evidence Management

An AI alert should not simply state:

> Something unusual happened.

The system should provide evidence.

Possible evidence:

```text
Annotated frame
Video clip
Timestamp
Bounding box
Trajectory
```

Example:

```text
Event:
Restricted Area Entry

Frame:
1269

Timestamp:
00:42.31

Track ID:
7

Bounding Box:
[120,80,220,350]
```

This makes the system explainable.

---

# 14. Analysis Job Tracking

Video processing can take time.

The backend tracks:

```text
Queued
Processing
Detection
Tracking
Behaviour Analysis
Event Generation
Completed
Failed
```

The frontend can show:

```text
Analysis: 72%

Current stage:
Behaviour Analysis
```

---

# 15. Timeline

The backend provides a chronological timeline.

Example:

```text
00:12
Person #3 walking

00:25
Person #7 enters restricted zone

00:42
Person #7 becomes stationary

00:57
Person #7 exits restricted zone
```

This gives the user temporal context rather than isolated detections.

---

# 16. Dashboard Summary

The backend provides statistics such as:

```text
People Detected: 12
Unique Tracks: 12
Normal Events: 31
Abnormal Events: 4
High-Risk Events: 2
Average Confidence: 91%
```

The backend calculates these values so the frontend does not need to process raw database data.

---

# 17. REST API

The frontend communicates with:

```text
/api/videos
/api/tracks
/api/behaviours
/api/events
/api/evidence
/api/analysis
/api/zones
```

Architecture:

```text
Frontend
    ↓
REST API
    ↓
Backend
    ↓
PostgreSQL
```

---

# 18. Why Frontend Does Not Directly Access PostgreSQL

The architecture intentionally uses:

```text
React
 ↓
FastAPI
 ↓
PostgreSQL
```

Reasons:

### Security

Database credentials stay server-side.

### Validation

The backend validates incoming data.

### Business Logic

Event processing remains centralized.

### Flexibility

Database changes do not require frontend changes.

---

# 19. Why PostgreSQL?

PostgreSQL was selected because the project has related entities and requires:

- Relationships
- Foreign keys
- Filtering
- Sorting
- Historical data
- Multiple videos
- Multiple tracks
- Events
- Evidence

JSON files are useful during prototyping, but PostgreSQL is more suitable as the final persistent store.

JSON/JSONB is still useful for flexible AI metadata.

---

# 20. Why Store Videos Outside PostgreSQL?

Video files can be large.

Instead:

```text
Video file
→ Filesystem / object storage

Video metadata
→ PostgreSQL
```

This keeps the database focused on structured application data.

---

# 21. Why FastAPI?

FastAPI was selected because:

- It is Python-based.
- The AI/CV pipeline is Python-based.
- It provides automatic API documentation.
- Pydantic provides validation.
- It integrates naturally with ML/CV components.
- It is straightforward for the frontend to consume.

The automatic documentation is available through:

```text
/docs
```

---

# 22. Why SQLAlchemy?

SQLAlchemy provides an ORM layer between Python and PostgreSQL.

Benefits:

- Database relationships
- Reusable models
- Cleaner queries
- Easier testing
- Reduced raw SQL
- Easier database maintenance

---

# 23. Why Alembic?

The database will evolve during development.

For example, later we may add:

```text
Action Recognition
Object Categories
Behaviour Embeddings
Camera Information
Review Feedback
```

Alembic allows these schema changes to be versioned and reproduced.

---

# 24. Why Mock Data?

All four team members are developing simultaneously.

Member 3 should not have to wait for Members 1 and 2.

Therefore the backend supports:

```text
Mock Track Data
Mock Behaviour Data
Mock Event Data
```

This allows parallel development.

Member 4 can also build the dashboard against mock API responses.

---

# 25. Stable Data Contracts

One of the most important design decisions is the use of stable data contracts.

Member 1 can change:

```text
YOLO version
Tracker
Detection algorithm
Frame sampling
```

without changing the backend database.

Member 2 can change:

```text
Rules
LSTM
Transformer
Vision-Language Model
```

without changing the database.

Only the output contract needs to remain compatible.

---

# 26. Member 1 Contract

Member 1 sends:

```json
{
  "track_id": 7,
  "object_type": "person",
  "timestamp": 42.31,
  "frame_number": 1269,
  "bbox": [120,80,220,350],
  "center": [170,215],
  "confidence": 0.94
}
```

The backend does not need to know how the tracking result was produced.

---

# 27. Member 2 Contract

Member 2 sends:

```json
{
  "track_id": 7,
  "behaviour_type": "restricted_area_entry",
  "start_time": 42.31,
  "end_time": 55.82,
  "confidence": 0.94,
  "classification": "abnormal",
  "reason": "Person entered restricted zone."
}
```

The backend validates, stores, and processes this information.

---

# 28. Member 4 Contract

Member 4 consumes:

```text
Video API
Track API
Behaviour API
Event API
Evidence API
Timeline API
Summary API
Analysis API
```

The frontend never needs direct database access.

---

# 29. Complete Data Flow

```text
1. User uploads video
            ↓
2. Backend creates Video record
            ↓
3. Analysis Job created
            ↓
4. Member 1 detects objects
            ↓
5. Member 1 tracks objects
            ↓
6. Track data enters backend
            ↓
7. PostgreSQL stores tracks
            ↓
8. Member 2 analyzes behaviour
            ↓
9. Behaviour data enters backend
            ↓
10. Backend stores behaviour
            ↓
11. Abnormal behaviour becomes Event
            ↓
12. Evidence is attached
            ↓
13. PostgreSQL stores everything
            ↓
14. Member 4 requests API
            ↓
15. Dashboard displays results
```

---

# 30. Example Complete Event

Suppose Person #7 enters a restricted area.

### Detection

```text
Person #7 detected
```

### Tracking

```text
Person #7
Position:
(120,200)
→
(150,230)
→
(190,270)
```

### Behaviour

```text
Person #7 crossed restricted-zone boundary.
```

### Backend

```text
Create Event
```

### Database

```text
Event ID:
EVT-101

Track:
7

Type:
restricted_area_entry

Time:
00:42.31

Confidence:
94%

Severity:
HIGH
```

### Evidence

```text
Frame:
1269

Timestamp:
00:42.31

Bounding Box:
[120,80,220,350]
```

### Dashboard

```text
HIGH

Person #7 entered restricted area

00:42

94% confidence

[View Evidence]
```

This demonstrates how all four members' work becomes one feature.

---

# 31. Why This Architecture Fits the Problem

The project is not simply:

> Detect people.

It requires understanding behaviour over time.

Therefore the system preserves:

```text
Object Identity
+
Position
+
Time
+
Behaviour
+
Event
+
Evidence
```

Persistent track history is therefore an important part of the architecture.

---

# 32. Scalability

The architecture can expand from:

```text
One video
```

to:

```text
Multiple videos
```

and later:

```text
Multiple cameras
```

The use of video IDs, track IDs, event IDs, and relational links keeps data isolated and organized.

---

# 33. Future Extensions

The architecture can support:

- Real-time camera streams
- RTSP cameras
- Multiple cameras
- Action recognition
- Deep anomaly detection
- Vision-Language Models
- Event notifications
- Email alerts
- Mobile notifications
- Authentication
- Role-based access
- Cloud object storage
- Advanced analytics
- Behaviour history

---

# 34. Security Considerations

The backend should:

- Keep database credentials private.
- Use environment variables.
- Validate uploaded files.
- Validate API requests.
- Prevent frontend direct database access.
- Avoid exposing stack traces.
- Restrict CORS origins.
- Prevent unsafe file paths.

For the hackathon prototype, basic security is sufficient.

---

# 35. Testing Strategy

### Unit Testing

Test:

```text
Services
Validation
Event logic
Database operations
```

### API Testing

Test:

```text
Upload
Import
Retrieve
Update
Delete
```

### Integration Testing

Test:

```text
Track
→ Behaviour
→ Event
→ Evidence
→ API
```

### End-to-End Testing

Test:

```text
Video
→ AI
→ Backend
→ Database
→ Dashboard
```

---

# 36. What Member 3 Owns

```text
✓ PostgreSQL
✓ Database design
✓ SQLAlchemy
✓ Alembic
✓ FastAPI
✓ API contracts
✓ Track storage
✓ Behaviour storage
✓ Event generation
✓ Evidence storage
✓ Analysis status
✓ Timeline API
✓ Summary API
✓ Integration
✓ Testing
✓ Docker
✓ Backend documentation
```

---

# 37. What Member 3 Does Not Own

```text
✗ YOLO model development
✗ Object detector training
✗ Tracker algorithm development
✗ Behaviour model training
✗ React UI design
✗ Frontend styling
```

These remain with the other members.

---

# 38. Design Philosophy

The backend follows four principles:

### 1. Separation of concerns

Each member owns a specific responsibility.

### 2. Stable interfaces

Modules communicate through predictable data contracts.

### 3. Evidence-first architecture

Important events retain timestamps and evidence.

### 4. Integration-first design

The backend connects the team's work rather than operating as an isolated application.

---

# 39. Final Architecture Summary

```text
                ┌──────────────────┐
                │      VIDEO       │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Detection        │
                │ + Tracking       │
                │    MEMBER 1      │
                └────────┬─────────┘
                         │
                    Track Data
                         │
                         ▼
                ┌──────────────────┐
                │ Behaviour        │
                │ Intelligence     │
                │    MEMBER 2      │
                └────────┬─────────┘
                         │
                  Behaviour Data
                         │
                         ▼
       ┌──────────────────────────────────┐
       │             MEMBER 3             │
       │                                  │
       │ FastAPI                          │
       │ PostgreSQL                       │
       │ Event Engine                     │
       │ Evidence                         │
       │ Timeline                         │
       │ Analysis Jobs                    │
       │ Integration                      │
       └────────────────┬─────────────────┘
                        │
                     REST API
                        │
                        ▼
                ┌──────────────────┐
                │    MEMBER 4      │
                │    Dashboard     │
                └──────────────────┘
```

---

# 40. Final Outcome

Member 3 transforms independently developed modules into one system.

The final backend maintains a chain of information:

```text
WHO
 ↓
Person #7

WHERE
 ↓
Restricted Area

WHAT
 ↓
Entered the restricted area

WHEN
 ↓
00:42.31

HOW CONFIDENT
 ↓
94%

WHY
 ↓
Crossed predefined zone boundary

PROOF
 ↓
Evidence Frame / Trajectory
```

This is the central purpose of the backend.

It does not replace the AI modules.

It connects, persists, structures, validates, and exposes their intelligence so the final system can demonstrate meaningful behaviour understanding rather than isolated detections.
