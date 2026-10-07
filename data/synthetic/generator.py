"""
Warehouse Sentinel - Synthetic Tracking Data Generator
Generates realistic spatio-temporal trajectories with bounding boxes and
COCO 17-keypoint skeletons for testing and simulation without requiring YOLO.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np


def create_upright_keypoints(
    cx: float, cy: float, height: float = 160.0, width: float = 60.0, conf: float = 0.95
) -> List[List[float]]:
    """Generate 17 COCO keypoints for an upright human subject."""
    top_y = cy - height / 2.0
    bot_y = cy + height / 2.0
    hw = width / 2.0

    return [
        [cx, top_y + 10, conf],                  # 0: nose
        [cx - 4, top_y + 7, conf],               # 1: left eye
        [cx + 4, top_y + 7, conf],               # 2: right eye
        [cx - 8, top_y + 8, conf],               # 3: left ear
        [cx + 8, top_y + 8, conf],               # 4: right ear
        [cx - hw * 0.7, top_y + 35, conf],       # 5: left shoulder
        [cx + hw * 0.7, top_y + 35, conf],       # 6: right shoulder
        [cx - hw * 0.85, top_y + 65, conf],      # 7: left elbow
        [cx + hw * 0.85, top_y + 65, conf],      # 8: right elbow
        [cx - hw * 0.9, top_y + 95, conf],       # 9: left wrist
        [cx + hw * 0.9, top_y + 95, conf],       # 10: right wrist
        [cx - hw * 0.45, top_y + 85, conf],      # 11: left hip
        [cx + hw * 0.45, top_y + 85, conf],      # 12: right hip
        [cx - hw * 0.45, top_y + 125, conf],     # 13: left knee (straight ~ 180 deg)
        [cx + hw * 0.45, top_y + 125, conf],     # 14: right knee
        [cx - hw * 0.45, bot_y - 5, conf],       # 15: left ankle
        [cx + hw * 0.45, bot_y - 5, conf],       # 16: right ankle
    ]


def create_sitting_keypoints(
    cx: float, cy: float, height: float = 100.0, width: float = 70.0, conf: float = 0.95
) -> List[List[float]]:
    """Generate 17 COCO keypoints for a sitting human subject (bent knees ~90-100 deg)."""
    top_y = cy - height / 2.0
    bot_y = cy + height / 2.0
    hw = width / 2.0

    # Hips are at chair level, knees are bent forward horizontally
    hip_y = top_y + 60
    knee_x_offset = 25.0
    knee_y = hip_y + 5
    ankle_y = bot_y - 5

    return [
        [cx, top_y + 8, conf],                   # 0: nose
        [cx - 4, top_y + 6, conf],               # 1: left eye
        [cx + 4, top_y + 6, conf],               # 2: right eye
        [cx - 7, top_y + 7, conf],               # 3: left ear
        [cx + 7, top_y + 7, conf],               # 4: right ear
        [cx - hw * 0.6, top_y + 28, conf],       # 5: left shoulder
        [cx + hw * 0.6, top_y + 28, conf],       # 6: right shoulder
        [cx - hw * 0.7, top_y + 45, conf],       # 7: left elbow
        [cx + hw * 0.7, top_y + 45, conf],       # 8: right elbow
        [cx - hw * 0.5, hip_y, conf],            # 9: left wrist on lap
        [cx + hw * 0.5, hip_y, conf],            # 10: right wrist on lap
        [cx - hw * 0.35, hip_y, conf],           # 11: left hip
        [cx + hw * 0.35, hip_y, conf],           # 12: right hip
        [cx - hw * 0.35 + knee_x_offset, knee_y, conf],  # 13: left knee (bent)
        [cx + hw * 0.35 + knee_x_offset, knee_y, conf],  # 14: right knee (bent)
        [cx - hw * 0.35 + knee_x_offset, ankle_y, conf], # 15: left ankle
        [cx + hw * 0.35 + knee_x_offset, ankle_y, conf], # 16: right ankle
    ]


def create_lying_keypoints(
    cx: float, cy: float, width: float = 170.0, height: float = 50.0, conf: float = 0.95
) -> List[List[float]]:
    """Generate 17 COCO keypoints for a horizontal lying human subject."""
    left_x = cx - width / 2.0
    right_x = cx + width / 2.0

    return [
        [left_x + 10, cy, conf],                 # 0: nose
        [left_x + 12, cy - 3, conf],             # 1: left eye
        [left_x + 12, cy + 3, conf],             # 2: right eye
        [left_x + 15, cy - 5, conf],             # 3: left ear
        [left_x + 15, cy + 5, conf],             # 4: right ear
        [left_x + 35, cy - 12, conf],            # 5: left shoulder
        [left_x + 35, cy + 12, conf],            # 6: right shoulder
        [left_x + 55, cy - 14, conf],            # 7: left elbow
        [left_x + 55, cy + 14, conf],            # 8: right elbow
        [left_x + 75, cy - 14, conf],            # 9: left wrist
        [left_x + 75, cy + 14, conf],            # 10: right wrist
        [left_x + 85, cy - 8, conf],             # 11: left hip
        [left_x + 85, cy + 8, conf],             # 12: right hip
        [left_x + 125, cy - 8, conf],            # 13: left knee
        [left_x + 125, cy + 8, conf],            # 14: right knee
        [right_x - 10, cy - 8, conf],            # 15: left ankle
        [right_x - 10, cy + 8, conf],            # 16: right ankle
    ]


def create_crouching_keypoints(
    cx: float, cy: float, height: float = 90.0, width: float = 70.0, conf: float = 0.95
) -> List[List[float]]:
    """Generate 17 COCO keypoints for a crouching / squatting subject (hips dropped low, deep knee flexion)."""
    top_y = cy - height / 2.0
    bot_y = cy + height / 2.0
    hw = width / 2.0

    # In deep squat/crouch, hips are close to ankles
    hip_y = bot_y - 25.0
    knee_x_offset = 20.0
    knee_y = bot_y - 28.0
    ankle_y = bot_y - 5.0

    return [
        [cx, top_y + 8, conf],                   # 0: nose
        [cx - 4, top_y + 6, conf],               # 1: left eye
        [cx + 4, top_y + 6, conf],               # 2: right eye
        [cx - 7, top_y + 7, conf],               # 3: left ear
        [cx + 7, top_y + 7, conf],               # 4: right ear
        [cx - hw * 0.6, top_y + 24, conf],       # 5: left shoulder
        [cx + hw * 0.6, top_y + 24, conf],       # 6: right shoulder
        [cx - hw * 0.7, top_y + 40, conf],       # 7: left elbow
        [cx + hw * 0.7, top_y + 40, conf],       # 8: right elbow
        [cx - hw * 0.5, hip_y, conf],            # 9: left wrist
        [cx + hw * 0.5, hip_y, conf],            # 10: right wrist
        [cx - hw * 0.35, hip_y, conf],           # 11: left hip
        [cx + hw * 0.35, hip_y, conf],           # 12: right hip
        [cx - hw * 0.35 + knee_x_offset, knee_y, conf],  # 13: left knee (deeply flexed < 100 deg)
        [cx + hw * 0.35 + knee_x_offset, knee_y, conf],  # 14: right knee
        [cx - hw * 0.35, ankle_y, conf],         # 15: left ankle
        [cx + hw * 0.35, ankle_y, conf],         # 16: right ankle
    ]


def create_bending_keypoints(
    cx: float, cy: float, height: float = 110.0, width: float = 85.0, conf: float = 0.95
) -> List[List[float]]:
    """Generate 17 COCO keypoints for a subject bending / stooping forward at waist with straight legs."""
    bot_y = cy + height / 2.0
    ankle_y = bot_y - 5.0
    knee_y = bot_y - 40.0
    hip_y = bot_y - 75.0

    # Hips are near center_x, torso leans forward to the right
    hip_x = cx - 15.0
    shoulder_x = hip_x + 38.0
    shoulder_y = hip_y - 18.0  # forward lean (torso angle ~ 55-65 deg from vertical)
    head_x = shoulder_x + 20.0
    head_y = shoulder_y - 5.0

    return [
        [head_x, head_y, conf],                  # 0: nose
        [head_x - 3, head_y - 3, conf],          # 1: left eye
        [head_x + 3, head_y - 3, conf],          # 2: right eye
        [head_x - 5, head_y - 2, conf],          # 3: left ear
        [head_x + 5, head_y - 2, conf],          # 4: right ear
        [shoulder_x, shoulder_y - 10, conf],     # 5: left shoulder
        [shoulder_x, shoulder_y + 10, conf],     # 6: right shoulder
        [shoulder_x + 10, shoulder_y + 20, conf],# 7: left elbow
        [shoulder_x + 10, shoulder_y + 20, conf],# 8: right elbow
        [shoulder_x + 15, shoulder_y + 40, conf],# 9: left wrist
        [shoulder_x + 15, shoulder_y + 40, conf],# 10: right wrist
        [hip_x, hip_y - 8, conf],                # 11: left hip
        [hip_x, hip_y + 8, conf],                # 12: right hip
        [hip_x, knee_y, conf],                   # 13: left knee (straight leg)
        [hip_x, knee_y, conf],                   # 14: right knee (straight leg)
        [hip_x, ankle_y, conf],                  # 15: left ankle
        [hip_x, ankle_y, conf],                  # 16: right ankle
    ]


def generate_standing_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    center_x: float = 200.0,
    center_y: float = 300.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a stationary standing person with slight micro-motion."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        # Natural slight micro-motion / pixel noise (< 1.5 px)
        cx = center_x + 0.8 * math.sin(i * 0.3)
        cy = center_y + 0.5 * math.cos(i * 0.3)
        w, h = 60.0, 160.0
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_upright_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_walking_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    start_x: float = 100.0,
    center_y: float = 300.0,
    velocity_px_s: float = 15.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a walking person moving horizontally at moderate velocity."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = start_x + (i * dt) * velocity_px_s
        cy = center_y + 1.0 * math.sin(i * 0.8)  # slight vertical bounce of walking
        w, h = 60.0, 160.0
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_upright_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_running_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    start_x: float = 50.0,
    center_y: float = 300.0,
    velocity_px_s: float = 38.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a running person moving rapidly at high velocity."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = start_x + (i * dt) * velocity_px_s
        cy = center_y + 2.5 * math.sin(i * 1.5)  # running vertical bounce
        w, h = 60.0, 155.0
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_upright_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_sitting_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    center_x: float = 250.0,
    center_y: float = 350.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a stationary sitting person with bent knees."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = center_x + 0.3 * math.sin(i * 0.2)
        cy = center_y
        w, h = 70.0, 100.0  # compact sitting bounding box
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_sitting_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_lying_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    center_x: float = 300.0,
    center_y: float = 400.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a stationary horizontal person lying on the floor."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = center_x
        cy = center_y
        w, h = 170.0, 50.0  # wide aspect ratio
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_lying_keypoints(cx, cy, w, h, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_crouching_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    center_x: float = 250.0,
    center_y: float = 350.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a stationary crouching / squatting person with deep knee flexion."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = center_x + 0.3 * math.sin(i * 0.2)
        cy = center_y
        w, h = 70.0, 90.0  # low vertical height
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_crouching_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_bending_sequence(
    track_id: int = 1,
    start_time: float = 0.0,
    duration: float = 3.0,
    fps: float = 10.0,
    center_x: float = 250.0,
    center_y: float = 330.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """Generate frames for a stationary bending / stooping person with straight legs and forward-tilted torso."""
    frames = []
    num_frames = int(duration * fps)
    dt = 1.0 / fps

    for i in range(num_frames):
        t = start_time + i * dt
        cx = center_x + 0.3 * math.sin(i * 0.2)
        cy = center_y
        w, h = 85.0, 110.0  # forward bent posture
        bbox = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]

        kpts = create_bending_keypoints(cx, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })
    return frames


def generate_fall_sequence(
    track_id: int = 1,
    start_time: float = 10.0,
    fps: float = 10.0,
    center_x: float = 300.0,
    standing_y: float = 250.0,
    floor_y: float = 400.0,
    include_keypoints: bool = True,
    confidence: float = 0.95,
) -> List[Dict[str, Any]]:
    """
    Generate realistic 4-phase temporal fall sequence:
    Phase 1: Standing (10.0s - 11.0s)
    Phase 2: Rapid downward descent + acceleration spike (11.0s - 11.5s)
    Phase 3: Impact & posture collapse to horizontal (11.5s - 11.8s)
    Phase 4: Post-fall stability / lying motionless (11.8s - 14.0s)
    """
    frames = []
    dt = 1.0 / fps

    # Phase 1: Standing for 1.2s (12 frames)
    for i in range(12):
        t = start_time + i * dt
        w, h = 60.0, 160.0
        cy = standing_y
        bbox = [center_x - w / 2, cy - h / 2, center_x + w / 2, cy + h / 2]
        kpts = create_upright_keypoints(center_x, cy, h, w, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })

    # Phase 2: Rapid downward descent (5 frames, ~0.5s, vertical drop ~120px -> ~240px/s)
    p2_frames = 5
    for i in range(1, p2_frames + 1):
        t = start_time + (11 + i) * dt
        prog = i / p2_frames
        # Non-linear drop accelerating downwards
        cy = standing_y + (floor_y - standing_y) * (prog ** 2)
        # Bounding box collapses in height and spreads horizontally
        h = 160.0 - 100.0 * prog
        w = 60.0 + 80.0 * prog
        bbox = [center_x - w / 2, cy - h / 2, center_x + w / 2, cy + h / 2]
        # Intermediate/tumbling keypoints transitioning from upright to horizontal
        if include_keypoints:
            kpts = (
                create_upright_keypoints(center_x, cy, h, w, conf=confidence)
                if prog < 0.5
                else create_lying_keypoints(center_x, cy, w, h, conf=confidence)
            )
        else:
            kpts = None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })

    # Phase 3 & 4: Post-fall lying motionless on floor for 2.2s (22 frames)
    p4_frames = 22
    for i in range(p4_frames):
        t = start_time + (16 + i) * dt
        w, h = 170.0, 50.0
        cy = floor_y
        bbox = [center_x - w / 2, cy - h / 2, center_x + w / 2, cy + h / 2]
        kpts = create_lying_keypoints(center_x, cy, w, h, conf=confidence) if include_keypoints else None
        frames.append({
            "track_id": track_id,
            "timestamp": round(t, 3),
            "bbox": bbox,
            "keypoints": kpts,
            "detection_confidence": confidence,
        })

    return frames


def generate_multi_person_sequence(
    duration: float = 3.0,
    fps: float = 10.0,
) -> List[List[Dict[str, Any]]]:
    """
    Generate interleaved frames for 3 simultaneous subjects:
    Person 1: Walking
    Person 2: Standing
    Person 3: Running
    """
    p1 = generate_walking_sequence(track_id=1, start_time=0.0, duration=duration, fps=fps, start_x=100.0)
    p2 = generate_standing_sequence(track_id=2, start_time=0.0, duration=duration, fps=fps, center_x=300.0)
    p3 = generate_running_sequence(track_id=3, start_time=0.0, duration=duration, fps=fps, start_x=50.0)

    # Interleave frame by frame
    interleaved_frames = []
    num_frames = min(len(p1), len(p2), len(p3))
    for i in range(num_frames):
        frame_group = [p1[i], p2[i], p3[i]]
        interleaved_frames.append(frame_group)

    return interleaved_frames
