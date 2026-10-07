"""
Warehouse Sentinel - Debug & Visualization Module
Draws bounding boxes, skeleton keypoints, motion trajectories, and behavioral
state overlays onto image frames for visual inspection and debugging.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Any
import numpy as np
import cv2

from .schemas import BehaviorResult, Keypoint, ActivityType, EventType

# COCO 17-keypoint skeleton connections (pairs of indices)
SKELETON_EDGES: List[Tuple[int, int]] = [
    (0, 1), (0, 2), (1, 3), (2, 4),        # Face
    (5, 6),                                # Shoulders
    (5, 7), (7, 9),                        # Left arm
    (6, 8), (8, 10),                       # Right arm
    (5, 11), (6, 12),                      # Torso
    (11, 12),                              # Hips
    (11, 13), (13, 15),                    # Left leg
    (12, 14), (14, 16),                    # Right leg
]

ACTIVITY_COLORS = {
    ActivityType.STANDING: (255, 180, 0),    # Amber
    ActivityType.WALKING: (0, 220, 0),       # Green
    ActivityType.RUNNING: (0, 140, 255),     # Orange
    ActivityType.SITTING: (200, 200, 0),     # Cyan-Yellow
    ActivityType.CROUCHING: (180, 50, 180),  # Purple
    ActivityType.BENDING: (0, 165, 255),     # Amber-Orange
    ActivityType.LYING: (255, 0, 255),       # Magenta
    ActivityType.FALLING: (0, 0, 255),       # Red
    ActivityType.UNKNOWN: (150, 150, 150),   # Gray
}


class BehaviorVisualizer:
    """Renders behavior diagnostics and overlays onto video frames."""

    def __init__(self, font_scale: float = 0.55, thickness: int = 2):
        self.font_scale = font_scale
        self.thickness = thickness

    def draw_result(
        self,
        frame: np.ndarray,
        result: BehaviorResult,
        bbox_coords: Optional[List[float]] = None,
        keypoints: Optional[List[Any]] = None,
    ) -> np.ndarray:
        """Draw behavior information, bounding box, and pose on frame."""
        img = frame.copy()
        color = ACTIVITY_COLORS.get(result.activity, (0, 255, 0))

        # 1. Draw Bounding Box
        if bbox_coords is not None and len(bbox_coords) == 4:
            x1, y1, x2, y2 = [int(v) for v in bbox_coords]
            cv2.rectangle(img, (x1, y1), (x2, y2), color, self.thickness)

            # Draw top banner
            vel_str = ""
            if result.motion_features:
                vel_str = f" | {result.motion_features.pixel_velocity:.1f}px/s"

            label = (
                f"ID:{result.track_id} {result.activity.value} "
                f"({result.confidence * 100:.0f}%){vel_str} [{result.activity_duration:.1f}s]"
            )

            (tw, th), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, 1
            )
            cv2.rectangle(img, (x1, max(0, y1 - th - 8)), (x1 + tw + 6, max(th + 8, y1)), color, -1)
            cv2.putText(
                img,
                label,
                (x1 + 3, max(12, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # Draw Event Banner if active
            if result.event:
                event_color = (0, 0, 255) if "FALL" in str(result.event.event_type) else (0, 140, 255)
                event_label = f"EVENT: {result.event.event_type} ({result.event.severity})"
                cv2.rectangle(img, (x1, y2), (x1 + tw + 6, y2 + th + 8), event_color, -1)
                cv2.putText(
                    img,
                    event_label,
                    (x1 + 3, y2 + th + 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self.font_scale,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        # 2. Draw Keypoints & Skeleton if present
        if keypoints is not None and len(keypoints) >= 17:
            self._draw_skeleton(img, keypoints)

        return img

    def _draw_skeleton(self, img: np.ndarray, keypoints: List[Any]) -> None:
        """Render 17-keypoint COCO skeleton."""
        parsed: List[Tuple[int, int, float]] = []
        for kp in keypoints:
            if isinstance(kp, Keypoint):
                parsed.append((int(kp.x), int(kp.y), kp.confidence))
            elif isinstance(kp, (list, tuple)):
                conf = kp[2] if len(kp) > 2 else 1.0
                parsed.append((int(kp[0]), int(kp[1]), float(conf)))

        # Draw skeleton limbs
        for p1_idx, p2_idx in SKELETON_EDGES:
            if p1_idx < len(parsed) and p2_idx < len(parsed):
                x1, y1, c1 = parsed[p1_idx]
                x2, y2, c2 = parsed[p2_idx]
                if c1 > 0.35 and c2 > 0.35:
                    cv2.line(img, (x1, y1), (x2, y2), (255, 200, 0), 2, cv2.LINE_AA)

        # Draw keypoint dots
        for x, y, conf in parsed:
            if conf > 0.35:
                cv2.circle(img, (x, y), 3, (0, 0, 255), -1, cv2.LINE_AA)
