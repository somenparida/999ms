# Autonomous Vision & Behaviour Understanding System

## Member 1: Vision Perception & Multi-Object Person Tracking Engine

This repository contains the complete **Member 1** implementation for the **Autonomous Vision & Behaviour Understanding System**. Member 1 delivers the foundational visual perception layer, providing real-time YOLO11n object/person detection, frame-by-frame video processing, and ByteTrack-based multi-person tracking with persistent track IDs and trajectory telemetry for downstream modules.

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
7. [Real-World Validation](#real-world-validation)
8. [Testing & Quality Assurance](#testing--quality-assurance)
9. [Known Limitations & Extensibility](#known-limitations--extensibility)

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
|   |  YOLO11n Detector | --> BBoxes, confidence, COCO class identification     |
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
│   │   ├── multi_person.mp4       # Real-world multi-person validation video
│   │   ├── test.mp4               # Benchmark test video
│   │   └── sample.jpg             # Single-frame test image
│   └── output/
│       ├── multi_person_tracked.mp4  # Annotated output with IDs & HUD
│       ├── test_detected.mp4         # Phase 2 video detection output
│       ├── test_tracked.mp4          # Phase 3 benchmark tracking output
│       └── tracks.json               # Member 1 -> Member 2 telemetry export
├── detection/
│   ├── __init__.py                # Package exports & lazy imports
│   ├── detector.py                # Phase 1: Reusable YOLODetector class
│   ├── video_detector.py          # Phase 2: VideoDetector class & CLI
│   └── tracker.py                 # Phase 3: PersonTracker & Member 2 adapters
├── models/
│   └── yolo11n.pt                 # YOLO11 nano model weights
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
& "D:\HackNex\venv\Scripts\python.exe" -m detection.tracker --input data/input/multi_person.mp4
```

*Optional Flags:*
- `--output <path>`: Custom output video path (default: `data/output/<stem>_tracked.mp4`).
- `--json-output <path>`: Custom telemetry JSON path (default: `data/output/tracks.json`).
- `--conf <float>`: Confidence threshold (default: `0.25`).

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
    "video_source": "D:\\hacknex\\autonomous-vision\\data\\input\\multi_person.mp4",
    "tracker": "ByteTrack",
    "model": "yolo11n.pt",
    "width": 640,
    "height": 480,
    "fps": 10.0,
    "total_frames": 20
  },
  "summary": {
    "total_records": 69,
    "unique_person_count": 4,
    "unique_track_ids": [1, 2, 3, 4]
  },
  "tracks": [
    {
      "track_id": 1,
      "timestamp": 0.0,
      "bbox": [42.72, 175.35, 194.88, 398.45],
      "keypoints": null,
      "detection_confidence": 0.8746,
      "frame_number": 1,
      "center": [118.8, 286.9],
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.8746
    }
  ]
}
```

### Field Definitions
| Field | Type | Description |
| :--- | :--- | :--- |
| `track_id` | `int` | Unique persistent identifier assigned to the person across frames. |
| `timestamp` | `float` | Elapsed video timeline in seconds calculated from native FPS ($(\text{frame}-1)/\text{FPS}$). |
| `bbox` | `list[float]` | Pixel coordinates `[x1, y1, x2, y2]`. |
| `keypoints` | `null` / `None` | Nullable field reserved for future pose estimation provider. |
| `detection_confidence` | `float` | YOLO detection confidence score (e.g. `0.8746`). |
| `frame_number` | `int` | 1-based sequential frame index. |
| `center` | `list[float]` | Midpoint coordinates `[cx, cy]` of the bounding box. |
| `class_id` | `int` | COCO class ID (`0` for person). |
| `class_name` | `str` | Class name string (`"person"`). |
| `confidence` | `float` | Backward-compatibility alias identical to `detection_confidence`. |

---

## Real-World Validation

The full tracking pipeline was validated on real multi-person video footage ([data/input/multi_person.mp4](file:///d:/hacknex/autonomous-vision/data/input/multi_person.mp4)):

```powershell
& "D:\HackNex\venv\Scripts\python.exe" -m detection.tracker --input data/input/multi_person.mp4
```

### Validation Metrics
- **Input Resolution:** `640 x 480 @ 10.0 FPS` (20 frames)
- **Processing Speed:** `11.78 FPS` (1.7 seconds total elapsed time)
- **Simultaneous Tracking:** 4 people tracked concurrently in frames 1–9; 3 people in frames 10–20.
- **Track ID Persistence:**
  - `Track ID 1`: Persisted across frames 1–20 (20/20 frames)
  - `Track ID 2`: Persisted across frames 1–20 (20/20 frames)
  - `Track ID 3`: Persisted across frames 1–20 (20/20 frames)
  - `Track ID 4`: Persisted across frames 1–9 (left boundary during camera pan)
- **Total Generated Records:** `69 records`
- **Output Artifacts:**
  - [data/output/multi_person_tracked.mp4](file:///d:/hacknex/autonomous-vision/data/output/multi_person_tracked.mp4) (Annotated video)
  - [data/output/tracks.json](file:///d:/hacknex/autonomous-vision/data/output/tracks.json) (Telemetry JSON)

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
