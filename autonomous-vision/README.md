# Autonomous Vision & Behaviour Understanding System

## Member 1: Vision Perception & Multi-Object Person Tracking Engine

This repository contains the complete **Member 1** implementation for the **Autonomous Vision & Behaviour Understanding System**. Member 1 delivers the foundational visual perception layer, providing real-time YOLO11n object/person detection, frame-by-frame video processing, and ByteTrack-based multi-person tracking with persistent track IDs and trajectory telemetry for downstream modules.

> **Note on Model & Architecture:**
> Member 1 utilizes the **pretrained YOLO11n model** from Ultralytics without custom training or fine-tuning. Keypoint/pose estimation is not currently performed by Member 1; the `keypoints` telemetry field is explicitly maintained as `null` as a reserved hook for future pose estimation modules.

---

## Table of Contents
1. [Architecture & Pipeline](#architecture--pipeline)
2. [Project Structure](#project-structure)
3. [Environment & Setup](#environment--setup)
4. [Implemented Phases](#implemented-phases)
   - [Phase 1: Image Object Detection](#phase-1-image-object-detection)
   - [Phase 2: Video Object Detection](#phase-2-video-object-detection)
   - [Phase 3: Multi-Person Tracking with ByteTrack](#phase-3-multi-person-tracking-with-bytetrack)
5. [Member 1 → Member 2 Integration Contract](#member-1--member-2-integration-contract)
6. [Telemetry Schema (`tracks.json`)](#telemetry-schema-tracksjson)
7. [Real-World Multi-Person Tracking Validation](#real-world-multi-person-tracking-validation)
8. [Testing & Quality Assurance](#testing--quality-assurance)
9. [Known Limitations & Extensibility](#known-limitations--extensibility)
10. [System Status & Member 2 Readiness](#system-status--member-2-readiness)

---

## Architecture & Pipeline

Member 1 serves as the visual sensor and tracking engine for the multi-member hackathon project:

```
+-------------------------------------------------------------------------------+
|                             MEMBER 1 MODULE                                   |
|                                                                               |
|  [ Video / Camera Stream ]                                                    |
|             |                                                                 |
|             v                                                                 |
|   +-------------------+                                                       |
|   |   OpenCV Ingest   | --> Frame extraction (native width, height, FPS)      |
|   +-------------------+                                                       |
|             |                                                                 |
|             v                                                                 |
|   +-------------------+                                                       |
|   |  YOLO11n Detector | --> Pretrained detection, bbox, conf, COCO class ID   |
|   +-------------------+                                                       |
|             |                                                                 |
|             v                                                                 |
|   +-------------------+                                                       |
|   | ByteTrack Engine  | --> Kalman filter + IoU association (Persistent IDs)  |
|   +-------------------+                                                       |
|             |                                                                 |
|             +-----------------------+-----------------------+                 |
|             |                                               |                 |
|             v                                               v                 |
|   [ Annotated Video ]                             [ Telemetry JSON ]          |
|   (data/output/*_tracked.mp4)                     (data/output/tracks.json)   |
+-------------------------------------------------------------|-----------------+
                                                              |
                                                              v
                                                +---------------------------+
                                                |      MEMBER 2 ENGINE      |
                                                |  behavior_engine.update() |
                                                |  - Loitering detection    |
                                                |  - Movement velocity      |
                                                |  - Abnormal behaviour     |
                                                +---------------------------+
```

---

## Project Structure

```text
D:\HackNex\autonomous-vision\
├── data/
│   ├── input/
│   │   ├── multi_person1.mp4      # High-density multi-person validation video
│   │   ├── multi_person.mp4       # Real-world benchmark video
│   │   ├── test.mp4               # Benchmark test video
│   │   └── sample.jpg             # Single-frame test image
│   └── output/
│       ├── multi_person1_tracked.mp4 # Annotated video with persistent IDs & HUD
│       ├── multi_person_tracked.mp4  # Initial multi-person validation video
│       ├── test_detected.mp4         # Phase 2 video detection output
│       ├── test_tracked.mp4          # Phase 3 tracking benchmark video
│       └── tracks.json               # Member 1 -> Member 2 telemetry export
├── detection/
│   ├── __init__.py                # Package exports & lazy imports
│   ├── detector.py                # Phase 1: Reusable YOLODetector class
│   ├── video_detector.py          # Phase 2: VideoDetector class & CLI
│   └── tracker.py                 # Phase 3: PersonTracker & Member 2 adapters
├── models/
│   └── yolo11n.pt                 # Pretrained YOLO11 nano model weights
├── tests/
│   ├── test_detector.py           # Phase 1 unit tests (5 tests)
│   ├── test_video_detector.py     # Phase 2 unit tests (6 tests)
│   └── test_tracker.py            # Phase 3 & integration unit tests (8 tests)
├── README.md                      # Comprehensive project documentation
└── requirements.txt               # Dependencies
```

---

## Environment & Setup

- **Operating System:** Windows
- **Python Version:** 3.11.6
- **Virtual Environment Path:** `D:\HackNex\venv`

### Dependencies (`requirements.txt`)
```text
ultralytics
opencv-python
numpy
pandas
matplotlib
lap>=0.5.12
```

---

## Implemented Phases

### Phase 1: Image Object Detection
Implemented in [detection/detector.py](file:///d:/hacknex/autonomous-vision/detection/detector.py).
- **Core Class:** `YOLODetector`
- **Features:**
  - Automated weights resolution (`models/yolo11n.pt` and workspace root).
  - Accepts image file paths or in-memory `numpy.ndarray` (BGR) frames.
  - Robust error handling for non-existent and corrupt files.
  - Standardized detection dictionary: `class_id`, `class_name`, `confidence`, and `bbox` `[x1, y1, x2, y2]`.
  - Built-in OpenCV bounding box rendering via `draw_detections`.

**Run Direct Inference Demo:**
```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m detection.detector
```

---

### Phase 2: Video Object Detection
Implemented in [detection/video_detector.py](file:///d:/hacknex/autonomous-vision/detection/video_detector.py).
- **Core Class:** `VideoDetector`
- **Features:**
  - Sequential frame extraction using OpenCV (`cv2.VideoCapture`).
  - Reuses underlying `YOLODetector` instance to avoid duplicate model overhead.
  - Special visual focus on the `person` class with custom badges and color palettes.
  - Real-time HUD banner displaying `Frame X/Y`, `Persons Count`, and `Total Objects`.
  - Strict preservation of input video geometry (width, height) and frame rate (FPS).
  - Multi-codec fallback for output encoding (`mp4v`, `avc1`, `XVID`, `MJPG`).

**Run Video Detection:**
```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m detection.video_detector --input data/input/test.mp4
```

*Optional Flags:*
- `--output <path>`: Custom destination for output video.
- `--conf <float>`: Detection confidence threshold (default: `0.25`).
- `--person-only`: Restricts detection and visualization strictly to people.
- `--classes <list>`: Filter by specific class names (e.g. `--classes person car`).

---

### Phase 3: Multi-Person Tracking with ByteTrack
Implemented in [detection/tracker.py](file:///d:/hacknex/autonomous-vision/detection/tracker.py).
- **Core Class:** `PersonTracker`
- **Tracking Algorithm:** Ultralytics ByteTrack integration (`bytetrack.yaml`).
  - Employs two-stage association: high-confidence detections are first matched to existing tracks, followed by low-confidence detections to recover occluded individuals without introducing false tracks.
- **Features:**
  - Restricts tracking to the COCO `person` class (`target_classes=[0]`).
  - Assigns persistent, sequential integer track IDs across frames.
  - Computes spatial center coordinates `[cx, cy]` for motion/velocity tracking.
  - Real-time video annotation with track-ID-seeded colors, label badges (`Person ID: X (conf)`), and top-left HUD.
  - Generates comprehensive telemetry exported to [data/output/tracks.json](file:///d:/hacknex/autonomous-vision/data/output/tracks.json).

**Run Person Tracking:**
```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m detection.tracker --input data/input/multi_person1.mp4 --conf 0.50
```

*Optional Flags:*
- `--output <path>`: Custom output video path (default: `data/output/<stem>_tracked.mp4`).
- `--json-output <path>`: Custom telemetry JSON path (default: `data/output/tracks.json`).
- `--conf <float>`: Confidence threshold (default: `0.25`).
- `--tracker-config <str>`: Tracker configuration (default: `bytetrack.yaml`).

---

## Member 1 → Member 2 Integration Contract

Member 1 establishes a strict data contract for Member 2's Behavior Engine. Downstream modules consume telemetry via the `behavior_engine.update(...)` interface:

```python
behavior_engine.update(
    track_id=record["track_id"],
    timestamp=record["timestamp"],
    bbox=record["bbox"],
    keypoints=record["keypoints"],
    detection_confidence=record["detection_confidence"],
)
```

### Provided Adapter Helpers
To eliminate boilerplate, Member 1 provides two integration utilities in `detection.tracker`:

```python
from detection.tracker import to_behavior_engine_kwargs, dispatch_to_behavior_engine

# Pattern 1: Unpack keyword arguments directly
kwargs = to_behavior_engine_kwargs(record)
behavior_engine.update(**kwargs)

# Pattern 2: Single-line dispatcher helper
dispatch_to_behavior_engine(behavior_engine, record)
```

---

## Telemetry Schema (`tracks.json`)

The exported JSON telemetry adheres to this structure:

```json
{
  "metadata": {
    "video_source": "D:\\hacknex\\autonomous-vision\\data\\input\\multi_person1.mp4",
    "tracker": "ByteTrack",
    "model": "yolo11n.pt",
    "width": 360,
    "height": 640,
    "fps": 30.0,
    "total_frames": 312
  },
  "summary": {
    "total_records": 849,
    "unique_person_count": 32,
    "unique_track_ids": [1, 2, 3, 4, 5, 6, 8, 10, 17, 18, 20, 24, 25, 26, 28, 29, 31, 33, 36, 38, 40, 41, 47, 48, 49, 56, 57, 58, 60, 61, 62, 64]
  },
  "tracks": [
    {
      "track_id": 1,
      "timestamp": 0.0,
      "bbox": [196.67, 244.99, 305.38, 506.5],
      "keypoints": null,
      "detection_confidence": 0.8983,
      "frame_number": 1,
      "center": [251.02, 375.75],
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.8983
    }
  ]
}
```

### Field Definitions
| Field | Type | Description |
| :--- | :--- | :--- |
| `track_id` | `int` | Unique persistent identifier assigned to the person across frames. |
| `timestamp` | `float` | Elapsed video timeline in seconds calculated from native FPS: $(\text{frame\_number}-1)/\text{FPS}$. |
| `bbox` | `list[float]` | Pixel coordinates `[x1, y1, x2, y2]`. |
| `keypoints` | `null` / `None` | Nullable field reserved for future pose estimation provider (currently unpopulated). |
| `detection_confidence` | `float` | YOLO detection confidence score (e.g. `0.8983`). |
| `frame_number` | `int` | 1-based sequential frame index. |
| `center` | `list[float]` | Midpoint coordinates `[cx, cy]` of the bounding box: $c_x = (x_1+x_2)/2$, $c_y = (y_1+y_2)/2$. |
| `class_id` | `int` | COCO class ID (`0` for person). |
| `class_name` | `str` | Class name string (`"person"`). |
| `confidence` | `float` | Backward-compatibility alias identical to `detection_confidence`. |

---

## Real-World Multi-Person Tracking Validation

The tracking pipeline was validated on multiple real-world videos without modifications to the architecture.

### Validation Benchmark Comparison

| Metric | `multi_person.mp4` (Baseline) | `multi_person1.mp4` (High-Density) |
| :--- | :--- | :--- |
| **Resolution** | $640 \times 480$ | $360 \times 640$ (Portrait) |
| **FPS** | $10.00\text{ FPS}$ | $30.00\text{ FPS}$ |
| **Total Frames** | $20\text{ frames}$ | $312\text{ frames}$ |
| **Video Duration** | $2.00\text{ seconds}$ | $10.40\text{ seconds}$ |
| **Confidence Threshold** | $0.50$ | $0.50$ |
| **Total Telemetry Records** | $69\text{ records}$ | $849\text{ records}$ |
| **Unique People Tracked\*** | $4\text{ individuals}$ | $32\text{ individuals}$ |
| **Max Simultaneous People** | $4\text{ people}$ | $6\text{ people}$ |
| **Avg Simultaneous People** | $3.45\text{ people/frame}$ | $3.03\text{ people/frame}$ |
| **Average Confidence** | $0.8402$ | $0.7528$ |
| **Processing Speed (CPU)** | $11.78\text{ FPS}$ | $17.44\text{ FPS}$ |
| **Output Video** | `data/output/multi_person_tracked.mp4` | `data/output/multi_person1_tracked.mp4` |

*\* Clarification: "32 unique people" denotes 32 distinct individuals observed and tracked across the entire 10.40-second video as people entered, crossed, and exited the scene, NOT 32 people simultaneously.*

---

### High-Density Validation Results (`multi_person1.mp4`)

**Validation Command:**
```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m detection.tracker --input data/input/multi_person1.mp4 --conf 0.50
```

#### 1. Execution & Video Metrics
- **Input Video:** `data/input/multi_person1.mp4`
- **Video Duration:** `10.40 seconds`
- **Resolution:** `360 × 640`
- **Original FPS:** `30.00 FPS`
- **Frames Processed:** `312 frames`
- **Processing Time:** `17.89 seconds`
- **Processing Speed:** `17.44 FPS on CPU`
- **Output Video:** [data/output/multi_person1_tracked.mp4](file:///d:/hacknex/autonomous-vision/data/output/multi_person1_tracked.mp4) (11.6 MB)
- **Telemetry Output:** [data/output/tracks.json](file:///d:/hacknex/autonomous-vision/data/output/tracks.json)

#### 2. Tracking & Detection Performance
- **Total Telemetry Records Generated:** `849 records`
- **Unique Individuals Tracked Across Video:** `32 individuals`
- **Simultaneous People per Frame:** Ranged from `1 to 6 people simultaneously` (mean: `3.03 people/frame`).
- **Confidence Threshold:** `0.50`
- **Minimum Detection Confidence:** `0.5004`
- **Maximum Detection Confidence:** `0.9404`
- **Average Detection Confidence:** `0.7528`

#### 3. Track ID Persistence Verification
Track IDs were assigned and maintained across consecutive frames while people remained trackable in the scene:
- **Track ID 41:** Persisted for **127 consecutive frames** (**4.23 seconds**)
- **Track ID 3:** Persisted for **100 frames** (**3.33 seconds**)
- **Track ID 6:** Persisted for **86 frames** (**2.87 seconds**)
- **Track ID 10:** Persisted for **64 frames** (**2.13 seconds**)
- **Track ID 2:** Persisted for **47 frames** (**1.57 seconds**)

#### 4. Geometry, Timing & Contract Validation
- **Bounding Boxes:** Verified as valid pixel coordinates `[x1, y1, x2, y2]` within image bounds.
- **Center Coordinates:** Verified with $0$ calculation errors across all $849$ records:
  $$\text{center} = \left[\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right]$$
- **Timestamps:** Accurately computed against the video timeline:
  $$\text{timestamp} = \frac{\text{frame\_number} - 1}{\text{FPS}}$$
- **Schema Adherence:** All $849$ records strictly adhere to the Member 1 → Member 2 integration schema.
- **Keypoints:** Explicitly maintained as `null` since Member 1 does not perform pose estimation.

---

### Representative Telemetry Records (`multi_person1.mp4`)

```json
[
  {
    "track_id": 1,
    "timestamp": 0.0,
    "bbox": [196.67, 244.99, 305.38, 506.5],
    "keypoints": null,
    "detection_confidence": 0.8983,
    "frame_number": 1,
    "center": [251.02, 375.75],
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.8983
  },
  {
    "track_id": 3,
    "timestamp": 0.63,
    "bbox": [86.62, 257.04, 116.68, 347.68],
    "keypoints": null,
    "detection_confidence": 0.5124,
    "frame_number": 20,
    "center": [101.65, 302.36],
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.5124
  },
  {
    "track_id": 10,
    "timestamp": 2.1,
    "bbox": [97.43, 318.93, 129.3, 414.97],
    "keypoints": null,
    "detection_confidence": 0.5664,
    "frame_number": 64,
    "center": [113.37, 366.95],
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.5664
  },
  {
    "track_id": 41,
    "timestamp": 6.13,
    "bbox": [8.7, 385.36, 48.32, 580.97],
    "keypoints": null,
    "detection_confidence": 0.7317,
    "frame_number": 185,
    "center": [28.51, 483.17],
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.7317
  }
]
```

---

## Testing & Quality Assurance

The codebase includes 19 automated unit tests covering all phases and contracts without requiring external large test files.

**Execute All Unit Tests:**
```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
```

### Test Suite Summary
| Test Module | Coverage Area | Status |
| :--- | :--- | :--- |
| `tests/test_detector.py` | Imports, YOLO11n loading, instantiation, synthetic inference, missing image error handling | **5 / 5 PASSED** |
| `tests/test_video_detector.py` | Model reuse, person-only filter, missing/corrupt video handling, frame annotation, synthetic end-to-end video I/O | **6 / 6 PASSED** |
| `tests/test_tracker.py` | Tracker init, person class restriction, center calculation, record schema, Member 2 adapter kwargs, mock behavior engine dispatch, synthetic video tracking & JSON schema | **8 / 8 PASSED** |
| **Total** | **All Modules & Contracts** | **19 / 19 PASSED** |

---

## Known Limitations & Extensibility

1. **Synthetic Frames vs. Real Person Weights:**
   YOLO11n weights are pretrained on real-world COCO imagery. Synthetic geometric shapes (e.g. flat colored rectangles) will not reliably trigger person detections or Kalman track persistence. Identity persistence must be evaluated on genuine video imagery of people in motion.
2. **Extended Visual Occlusions:**
   Standard ByteTrack uses spatial Kalman filtering and bounding box IoU. If an individual is fully occluded for longer than the tracklet buffer window, a new track ID may be assigned upon re-emergence. Deep appearance Re-ID embeddings can be layered on top if prolonged occlusions occur.
3. **Keypoints / Pose Estimation Extension:**
   The `keypoints` field in each tracking record is currently set to `null` (`None`). The architecture is designed to allow a pose estimation provider (e.g. YOLO11-pose) to populate this field without breaking Member 2's `behavior_engine.update(...)` interface.

---

## System Status & Member 2 Readiness

Member 1's person detection and multi-person tracking pipeline has been thoroughly validated on multiple real-world videos and is **fully verified and ready for Member 2 integration**:

- **Real-World Multi-Person Tracking:** Successfully tracks multiple people simultaneously with persistent track IDs.
- **Telemetry Export:** Generates standardized JSON telemetry with pixel bboxes, centers, timestamps, and detection confidences.
- **Integration Adapters:** Ready-to-use helpers (`to_behavior_engine_kwargs`, `dispatch_to_behavior_engine`) for direct consumption by Member 2's Behavior Engine.
- **Zero Architectural Regressions:** All 19 unit tests pass cleanly in ~2 seconds.
