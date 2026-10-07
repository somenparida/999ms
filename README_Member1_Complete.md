# Autonomous Vision & Behaviour Understanding System

## Member 1 --- Person Detection, Multi-Person Tracking & Telemetry

Member 1 provides the visual perception and tracking layer of the
system. It detects people with pretrained YOLO11n, tracks multiple
people with ByteTrack, and produces structured telemetry for Member 2's
behavior engine.

> Member 1 does **not** perform behavior classification, abnormal-event
> detection, or pose estimation.

## 1. Responsibilities

-   YOLO11n person detection
-   Frame-by-frame video processing
-   Multi-person ByteTrack tracking
-   Persistent `track_id` while a track is maintained
-   Pixel-coordinate bounding boxes
-   Center coordinates
-   Video-timeline timestamps
-   YOLO detection confidence
-   Structured telemetry JSON
-   Member 1 → Member 2 adapters
-   Annotated videos
-   Automated tests and real-world validation

## 2. Architecture

``` text
Input Video
    ↓
OpenCV Ingestion
    ↓
YOLO11n Person Detection
    ↓
ByteTrack Multi-Person Tracking
    ↓
Bounding Boxes + Track IDs + Timestamps + Confidence
    ↓
Telemetry JSON / Annotated MP4
    ↓
Member 2 Behavior Engine
```

## 3. Project Structure

``` text
autonomous-vision/
├── detection/
│   ├── __init__.py
│   ├── detector.py
│   ├── video_detector.py
│   ├── tracker.py
│   └── backend_exporter.py
├── data/
│   ├── input/
│   │   ├── multi_person.mp4
│   │   ├── multi_person1.mp4
│   │   ├── multi_person2.mp4
│   │   └── store.mp4
│   └── output/
│       ├── multi_person_tracked.mp4
│       ├── multi_person1_tracked.mp4
│       ├── multi_person2_tracked.mp4
│       ├── store_tracked.mp4
│       ├── tracks.json
│       ├── tracks_multi_person2.json
│       └── tracks_store.json
├── models/
│   └── yolo11n.pt
├── tests/
│   ├── test_detector.py
│   ├── test_video_detector.py
│   ├── test_tracker.py
│   └── test_backend_exporter.py
├── requirements.txt
└── README.md
```

## 4. Environment

``` text
Python 3.11.6
Virtual environment: D:\HackNex\venv
```

Core dependencies:

``` text
ultralytics
opencv-python
numpy
pandas
matplotlib
lap>=0.5.12
```

The project uses pretrained `yolo11n.pt`. Member 1 has **not**
fine-tuned or trained YOLO11n.

## 5. Phase 1 --- Image Detection

`detection/detector.py` provides `YOLODetector`.

It supports:

-   YOLO11n model loading
-   Image file paths
-   In-memory NumPy arrays
-   Standardized detections
-   Missing-input validation

Detection fields:

``` text
class_id
class_name
confidence
bbox
```

The target COCO class is:

``` text
class_id = 0
class_name = person
```

## 6. Phase 2 --- Video Detection

`detection/video_detector.py` processes videos sequentially with OpenCV.

It:

-   Runs YOLO detection frame-by-frame
-   Annotates detections
-   Highlights persons
-   Displays confidence scores
-   Preserves input resolution and FPS
-   Uses codec fallbacks: `mp4v`, `avc1`, `XVID`, `MJPG`

Example:

``` powershell
python -m detection.video_detector --input data/input/test.mp4
```

## 7. Phase 3 --- Multi-Person Tracking

`detection/tracker.py` combines YOLO11n with Ultralytics ByteTrack:

``` text
YOLO11n → Person Detection → ByteTrack → Persistent Track IDs → Telemetry
```

The tracker uses:

``` text
tracker = bytetrack.yaml
target class = COCO person (ID 0)
```

It supports simultaneous people and preserves IDs while tracks remain
recoverable.

### Coordinates

Bounding boxes:

``` text
[x1, y1, x2, y2]
```

Center:

``` text
cx = (x1 + x2) / 2
cy = (y1 + y2) / 2
```

### Timestamp

``` text
timestamp = (frame_number - 1) / FPS
```

### Confidence

`detection_confidence` comes directly from YOLO11n.

## 8. Member 1 → Member 2 Contract

Member 2 can consume records conceptually as:

``` python
behavior_engine.update(
    track_id=7,
    timestamp=12.4,
    bbox=[100, 100, 180, 300],
    keypoints=None,
    detection_confidence=0.94
)
```

Final record:

``` json
{
  "track_id": 7,
  "timestamp": 12.4,
  "bbox": [100, 100, 180, 300],
  "keypoints": null,
  "detection_confidence": 0.94,
  "frame_number": 372,
  "center": [140, 200],
  "class_id": 0,
  "class_name": "person"
}
```

### Fields

  Field                    Description
  ------------------------ ------------------------------------------------
  `track_id`               Persistent ByteTrack identity
  `timestamp`              Video timeline timestamp in seconds
  `bbox`                   Pixel coordinates `[x1,y1,x2,y2]`
  `keypoints`              Reserved for pose estimation; currently `null`
  `detection_confidence`   YOLO confidence
  `frame_number`           Source frame
  `center`                 `[cx,cy]` center of bounding box
  `class_id`               `0` for person
  `class_name`             `"person"`

## 9. Integration Helpers

``` python
from detection.tracker import to_behavior_engine_kwargs

for record in records:
    behavior_engine.update(**to_behavior_engine_kwargs(record))
```

Or:

``` python
from detection.tracker import dispatch_to_behavior_engine

for record in records:
    dispatch_to_behavior_engine(behavior_engine, record)
```

Explicit mapping:

``` python
behavior_engine.update(
    track_id=record["track_id"],
    timestamp=record["timestamp"],
    bbox=record["bbox"],
    keypoints=record["keypoints"],
    detection_confidence=record["detection_confidence"],
)
```

No behavior engine is implemented by Member 1.

## 10. Keypoints

Pose estimation is not currently implemented.

Therefore:

``` json
"keypoints": null
```

No keypoints are fabricated. The field is reserved for a future
pose/keypoint provider.

## 11. Running the Tracker

``` powershell
python -m detection.tracker --input data/input/multi_person.mp4 --conf 0.50
```

Custom output:

``` powershell
python -m detection.tracker --input data/input/multi_person2.mp4 --output data/output/multi_person2_tracked.mp4 --json-output data/output/tracks_multi_person2.json --conf 0.50
```

## 12. Real-World Validation

All validation runs used the existing YOLO11n + ByteTrack pipeline with
confidence threshold `0.50`.

### `multi_person.mp4`

Baseline benchmark:

``` text
640 × 480
10.00 FPS
20 frames
2.00 seconds
69 telemetry records
4 unique people
4 maximum simultaneous
3.45 average simultaneous/frame
0.7200 minimum confidence
0.9100 maximum confidence
0.8402 average confidence
11.78 FPS CPU
20 frames / 2.00 s longest tracklet
```

Output:

``` text
data/output/multi_person_tracked.mp4
data/output/tracks.json
```

### `multi_person1.mp4`

High-density walkway:

``` text
360 × 640
30.00 FPS
312 frames
10.40 seconds
849 telemetry records
32 unique people across the video
6 maximum simultaneous
3.03 average simultaneous/frame
0.5004 minimum confidence
0.9404 maximum confidence
0.7528 average confidence
17.44 FPS CPU
```

Longest observed tracklets:

``` text
Track 41: 127 frames / 4.23 s
Track 3:  100 frames / 3.33 s
Track 6:   86 frames / 2.87 s
Track 10:  64 frames / 2.13 s
Track 2:   47 frames / 1.57 s
```

Output:

``` text
data/output/multi_person1_tracked.mp4
data/output/tracks.json
```

### `multi_person2.mp4`

Pedestrian plaza:

``` text
368 × 368
30.08 FPS
608 frames
20.21 seconds
2,783 telemetry records
37 unique people across the video
8 maximum simultaneous
4.58 average simultaneous/frame
0.5001 minimum confidence
0.9205 maximum confidence
0.7204 average confidence
12.07 FPS CPU
```

Longest observed tracklets:

``` text
Track 24: 354 frames / 11.77 s
Track 37: 313 frames / 10.41 s
Track 47: 265 frames / 8.81 s
Track 30: 195 frames / 6.48 s
Track 14: 171 frames / 5.68 s
```

All 2,783 records passed:

``` text
Bounding-box validation: 0 errors
Center-coordinate validation: 0 errors
Timestamp validation: 0 errors
Member 1 → Member 2 schema validation: 0 errors
```

Output:

``` text
data/output/multi_person2_tracked.mp4
data/output/tracks_multi_person2.json
```

### `store.mp4`

Indoor retail/CCTV-style validation:

``` text
852 × 480
30.00 FPS
954 frames
31.80 seconds
5,396 telemetry records
51 unique people across the video
9 maximum simultaneous
5.66 average simultaneous/frame
0.5001 minimum confidence
0.9340 maximum confidence
0.7071 average confidence
16.50 FPS CPU
836 frames / 27.87 s longest tracklet
```

Output:

``` text
data/output/store_tracked.mp4
data/output/tracks_store.json
```

## 13. Benchmark Comparison

  ----------------------------------------------------------------------------
  Metric           multi_person   multi_person1   multi_person2          store
  -------------- -------------- --------------- --------------- --------------
  Scene                Baseline    High-Density      Pedestrian         Indoor
                                        Walkway           Plaza     Store/CCTV

  Resolution            640×480         360×640         368×368        852×480

  FPS                     10.00           30.00           30.08          30.00

  Frames                     20             312             608            954

  Duration               2.00 s         10.40 s         20.21 s        31.80 s

  Confidence               0.50            0.50            0.50           0.50
  threshold                                                     

  Telemetry                  69             849           2,783          5,396
  records                                                       

  Unique people               4              32              37             51

  Max                         4               6               8              9
  simultaneous                                                  

  Avg                      3.45            3.03            4.58           5.66
  simultaneous                                                  

  Min confidence         0.7200          0.5004          0.5001         0.5001

  Max confidence         0.9100          0.9404          0.9205         0.9340

  Avg confidence         0.8402          0.7528          0.7204         0.7071

  Longest           20 frames /    127 / 4.23 s   354 / 11.77 s  836 / 27.87 s
  tracklet               2.00 s                                 

  CPU speed           11.78 FPS       17.44 FPS       12.07 FPS      16.50 FPS
  ----------------------------------------------------------------------------

> Unique people means people assigned track IDs over the full video, not
> simultaneous people.

## 14. Quality Assurance

Automated test coverage:

``` text
test_detector.py
5 / 5 passed

test_video_detector.py
6 / 6 passed

test_tracker.py
8 / 8 passed

test_backend_exporter.py
3 / 3 passed
```

Overall:

``` text
22 / 22 tests passed
100% pass rate
```

The tracker tests cover initialization, person-only configuration,
center calculation, telemetry schema, Member 2 adapter mapping, mock
dispatch, missing-video handling, and end-to-end JSON generation.

## 15. Backend Exporter

The broader project includes:

``` text
detection/backend_exporter.py
```

for REST integration with the backend.

Documented endpoints:

``` text
/api/videos/{video_id}/tracks/import
/api/videos/{video_id}/analyze
```

This is separate from the core Member 1 tracking responsibility.

## 16. Occlusion and Tracking Limitations

ByteTrack can recover short-term interruptions using motion prediction
and association. Prolonged complete occlusion can terminate a tracklet,
after which a reappearing person may receive a new ID.

The current system does not add a separate deep appearance Re-ID model,
so difficult crowding, prolonged occlusion, or visually similar people
can cause ID switches or new IDs.

## 17. Design Decisions

### YOLO11n

A lightweight pretrained object detector suitable for the
person-detection stage.

### ByteTrack

Provides multi-object temporal association and persistent track IDs
without adding behavior classification to Member 1.

### Person-only detection

The pipeline targets COCO class `0`, `person`, because the downstream
task is human behavior understanding.

### Structured telemetry

Member 2 needs identity, time, location, bounding box, and confidence
rather than isolated frame detections.

## 18. Member Responsibilities

### Member 1

``` text
Person Detection
Person Localization
Bounding Boxes
Multi-Person Tracking
Track Identity
Coordinates
Timestamps
Detection Confidence
Telemetry
```

### Member 2

``` text
Behavior Detection
Behavior Classification
Abnormal Event Detection
Behavior-Level Decisions
```

## 19. Current Status

Member 1 has been validated across:

-   Short baseline video
-   High-density pedestrian video
-   Longer multi-person video
-   Indoor retail/CCTV-style video
-   Scenes with up to 9 simultaneously tracked people
-   Long tracklets up to 27.87 seconds

The pipeline has:

``` text
YOLO11n
    ↓
Person Detection
    ↓
ByteTrack
    ↓
Persistent Multi-Person Tracking
    ↓
Bounding Boxes + Centers + Timestamps + Confidence
    ↓
Structured Telemetry
    ↓
Member 2 Behavior Engine
```

The Member 1 → Member 2 contract is stable and documented, and the
automated test suite reports:

``` text
22 / 22 tests passed
100% pass rate
```

Member 1 is ready for downstream behavior analysis integration.
