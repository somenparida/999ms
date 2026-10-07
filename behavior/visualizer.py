"""
Warehouse Sentinel - Debug & Visualization Module
Draws bounding boxes, skeleton keypoints, motion trajectories, and behavioral
state overlays onto image frames for visual inspection and debugging.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Any
import numpy as np
import cv2

from .schemas import BehaviorResult, Keypoint, ActivityType, EventType, BehaviorStatus

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

STATUS_COLORS = {
    BehaviorStatus.NORMAL: (0, 200, 0),               # Green
    BehaviorStatus.POTENTIALLY_UNUSUAL: (0, 165, 255), # Amber / Orange
    BehaviorStatus.ABNORMAL: (0, 0, 255),             # Red
    BehaviorStatus.UNKNOWN: (150, 150, 150),          # Gray
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

    def draw_integrated_frame(
        self,
        frame: np.ndarray,
        records_with_results: List[Tuple[Dict[str, Any], BehaviorResult]],
        frame_number: int = 1,
        total_frames: int = 1,
        fps: float = 30.0,
    ) -> np.ndarray:
        """Render multi-person bounding boxes, behavioral diagnostics, and top-level HUD.

        Args:
            frame: Raw BGR frame.
            records_with_results: List of (track_record, BehaviorResult) pairs.
            frame_number: Current frame index.
            total_frames: Total frames in video.
            fps: Video frames per second.

        Returns:
            Fully annotated BGR frame.
        """
        img = frame.copy()
        h, w = img.shape[:2]

        normal_count = 0
        unusual_count = 0
        abnormal_count = 0
        active_critical_alerts: List[str] = []

        for record, result in records_with_results:
            bbox = record["bbox"]
            conf = record.get("detection_confidence", record.get("confidence", 1.0))
            kps = record.get("keypoints", None)

            # Classify status counts
            if result.status == BehaviorStatus.NORMAL:
                normal_count += 1
            elif result.status == BehaviorStatus.POTENTIALLY_UNUSUAL:
                unusual_count += 1
            elif result.status == BehaviorStatus.ABNORMAL:
                abnormal_count += 1
                reason_str = ", ".join(result.reasons) if result.reasons else "ABNORMAL BEHAVIOR"
                active_critical_alerts.append(f"Track {result.track_id}: {reason_str}")

            # Determine box color
            if result.status == BehaviorStatus.ABNORMAL:
                box_color = (0, 0, 255)  # Bright Red
            elif result.status == BehaviorStatus.POTENTIALLY_UNUSUAL:
                box_color = (0, 165, 255)  # Amber
            else:
                box_color = ACTIVITY_COLORS.get(result.activity, (0, 220, 0))

            x1, y1, x2, y2 = [int(v) for v in bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), box_color, self.thickness)

            # 1. Main Header Label: ID, Confidence, Activity, Duration, Velocity
            vel_str = ""
            if result.motion_features:
                vel_str = f" | {result.motion_features.pixel_velocity:.1f}px/s"

            label_top = f"ID:{result.track_id} ({conf * 100:.0f}%) {result.activity.value} [{result.activity_duration:.1f}s]{vel_str}"
            (tw, th), _ = cv2.getTextSize(label_top, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)

            cv2.rectangle(img, (x1, max(0, y1 - th - 8)), (x1 + tw + 6, max(th + 8, y1)), box_color, -1)
            cv2.putText(
                img,
                label_top,
                (x1 + 3, max(10, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # 2. Status Badge under top box header
            status_text = f"[{result.status.value}]"
            (sw, sh), _ = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
            status_bg = STATUS_COLORS.get(result.status, (150, 150, 150))
            cv2.rectangle(img, (x1, min(h - 1, y1 + 2)), (x1 + sw + 6, min(h - 1, y1 + sh + 8)), status_bg, -1)
            cv2.putText(
                img,
                status_text,
                (x1 + 3, min(h - 3, y1 + sh + 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # 3. Draw Event Banner if active
            if result.event:
                event_color = (0, 0, 255) if "FALL" in str(result.event.event_type) else (0, 140, 255)
                event_label = f"EVENT: {result.event.event_type} ({result.event.severity})"
                (ew, eh), _ = cv2.getTextSize(event_label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
                cv2.rectangle(img, (x1, min(h - 1, y2)), (x1 + ew + 6, min(h - 1, y2 + eh + 8)), event_color, -1)
                cv2.putText(
                    img,
                    event_label,
                    (x1 + 3, min(h - 4, y2 + eh + 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.42,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

            # 4. Draw Skeleton if available
            if kps is not None and len(kps) >= 17:
                self._draw_skeleton(img, kps)

        # Draw Top HUD Banner across width
        hud_h = 32
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, hud_h), (25, 25, 25), -1)
        cv2.addWeighted(overlay, 0.80, img, 0.20, 0, img)

        hud_text = (
            f"WAREHOUSE SENTINEL | Frame: {frame_number}/{total_frames} ({fps:.1f} FPS) | "
            f"Tracks: {len(records_with_results)} | "
            f"Norm: {normal_count} | Unus: {unusual_count} | Alert: {abnormal_count}"
        )
        cv2.putText(
            img,
            hud_text,
            (10, 21),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.46,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        # Draw Critical Alert Banner if any abnormal tracks
        if active_critical_alerts:
            alert_bar_h = 26
            alert_y = hud_h
            alert_overlay = img.copy()
            cv2.rectangle(alert_overlay, (0, alert_y), (w, alert_y + alert_bar_h), (0, 0, 180), -1)
            cv2.addWeighted(alert_overlay, 0.85, img, 0.15, 0, img)
            first_alert = active_critical_alerts[0]
            alert_str = f"CRITICAL SAFETY ALERT >> {first_alert.upper()}"
            cv2.putText(
                img,
                alert_str,
                (10, alert_y + 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.46,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return img
