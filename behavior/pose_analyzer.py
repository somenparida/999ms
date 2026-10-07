"""
Warehouse Sentinel - Pose Feature Extractor
Extracts body angles, aspect ratios, and posture metrics from standard
COCO/YOLO 17-keypoint skeletons with robust fallbacks.
"""

from __future__ import annotations
import math
from typing import List, Optional, Tuple, Any
import numpy as np

from .schemas import Keypoint, BoundingBox, PoseFeatures
from .config import PoseConfig

# COCO 17-keypoint semantic indices
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW = 7
RIGHT_ELBOW = 8
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12
LEFT_KNEE = 13
RIGHT_KNEE = 14
LEFT_ANKLE = 15
RIGHT_ANKLE = 16


class PoseAnalyzer:
    """Analyzes human posture geometry and joint configurations."""

    def __init__(self, config: PoseConfig):
        self.config = config

    def extract_features(
        self,
        keypoints: Optional[Any],
        bbox: BoundingBox,
    ) -> PoseFeatures:
        """Extract posture features from keypoints, falling back to bbox geometry if absent."""
        # Baseline bbox aspect ratio fallback
        bbox_w = bbox.width
        bbox_h = bbox.height
        fallback_aspect_ratio = bbox.aspect_ratio

        if keypoints is None:
            return PoseFeatures(
                available=False,
                body_width=bbox_w,
                body_height=bbox_h,
                aspect_ratio=fallback_aspect_ratio,
                pose_confidence=0.0,
            )

        # Parse keypoints into standard list of Keypoint objects
        parsed_kpts: List[Keypoint] = []
        try:
            for item in keypoints:
                if isinstance(item, Keypoint):
                    parsed_kpts.append(item)
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    parsed_kpts.append(Keypoint.from_iterable(item))
                elif isinstance(item, dict) and "x" in item and "y" in item:
                    parsed_kpts.append(
                        Keypoint(
                            x=float(item["x"]),
                            y=float(item["y"]),
                            confidence=float(item.get("confidence", 1.0)),
                        )
                    )
        except Exception:
            return PoseFeatures(
                available=False,
                body_width=bbox_w,
                body_height=bbox_h,
                aspect_ratio=fallback_aspect_ratio,
                pose_confidence=0.0,
            )

        if len(parsed_kpts) < 17:
            # Incomplete skeleton representation; fallback
            return PoseFeatures(
                available=False,
                body_width=bbox_w,
                body_height=bbox_h,
                aspect_ratio=fallback_aspect_ratio,
                pose_confidence=0.0,
            )

        # Filter valid keypoints based on confidence threshold
        conf_thresh = self.config.min_keypoint_confidence
        valid_kpts = [k for k in parsed_kpts if k.confidence >= conf_thresh]
        valid_ratio = len(valid_kpts) / 17.0

        if valid_ratio < self.config.min_valid_keypoint_ratio:
            # Insufficient valid keypoints to trust pose estimation
            return PoseFeatures(
                available=False,
                body_width=bbox_w,
                body_height=bbox_h,
                aspect_ratio=fallback_aspect_ratio,
                pose_confidence=float(np.mean([k.confidence for k in parsed_kpts])),
            )

        mean_conf = float(np.mean([k.confidence for k in valid_kpts]))
        overall_pose_conf = mean_conf * valid_ratio

        # Calculate bounding extents from valid keypoints
        xs = [k.x for k in valid_kpts]
        ys = [k.y for k in valid_kpts]
        horizontal_extent = max(xs) - min(xs)
        vertical_extent = max(ys) - min(ys)
        kpt_aspect_ratio = (
            (horizontal_extent / vertical_extent) if vertical_extent > 1e-4 else fallback_aspect_ratio
        )

        normalized_height = (
            (vertical_extent / bbox_h) if bbox_h > 1e-4 else 1.0
        )

        # Joint angle calculations
        torso_angle = self._calculate_torso_angle(parsed_kpts, conf_thresh)
        hip_angle = self._calculate_hip_angle(parsed_kpts, conf_thresh)
        knee_angle = self._calculate_knee_angle(parsed_kpts, conf_thresh)
        shoulder_angle = self._calculate_shoulder_angle(parsed_kpts, conf_thresh)
        hip_ankle_ratio = self._calculate_hip_ankle_ratio(parsed_kpts, vertical_extent, conf_thresh)

        return PoseFeatures(
            available=True,
            body_width=float(horizontal_extent),
            body_height=float(vertical_extent),
            aspect_ratio=float(kpt_aspect_ratio),
            torso_angle_deg=torso_angle,
            hip_angle_deg=hip_angle,
            knee_angle_deg=knee_angle,
            shoulder_angle_deg=shoulder_angle,
            vertical_extent=float(vertical_extent),
            horizontal_extent=float(horizontal_extent),
            normalized_height=float(normalized_height),
            hip_ankle_dy_ratio=float(hip_ankle_ratio),
            pose_confidence=round(overall_pose_conf, 4),
        )

    def _calculate_torso_angle(
        self, kpts: List[Keypoint], conf_thresh: float
    ) -> float:
        """
        Torso inclination angle relative to vertical axis in degrees.
        0 deg = perfectly upright, 90 deg = horizontal.
        Vector from midpoint of hips to midpoint of shoulders.
        """
        ls, rs = kpts[LEFT_SHOULDER], kpts[RIGHT_SHOULDER]
        lh, rh = kpts[LEFT_HIP], kpts[RIGHT_HIP]

        # Ensure at least one shoulder and one hip are valid
        valid_shoulders = [s for s in (ls, rs) if s.confidence >= conf_thresh]
        valid_hips = [h for h in (lh, rh) if h.confidence >= conf_thresh]

        if not valid_shoulders or not valid_hips:
            return 0.0

        mid_sx = float(np.mean([s.x for s in valid_shoulders]))
        mid_sy = float(np.mean([s.y for s in valid_shoulders]))
        mid_hx = float(np.mean([h.x for h in valid_hips]))
        mid_hy = float(np.mean([h.y for h in valid_hips]))

        # Vector pointing from hips upwards to shoulders
        dx = mid_sx - mid_hx
        dy = mid_sy - mid_hy  # Typically negative since screen y increases downwards

        # Angle from vertical (which has dx=0, dy < 0)
        # Using atan2: 0 deg when vertical upwards
        angle_rad = abs(math.atan2(dx, -dy))
        return float(math.degrees(angle_rad))

    def _calculate_knee_angle(
        self, kpts: List[Keypoint], conf_thresh: float
    ) -> float:
        """
        Calculate leg knee flexion angle (hip-knee-ankle) in degrees.
        Returns the more confident leg angle or average of valid legs.
        Straight leg ~ 180 deg, sitting ~ 90 deg.
        """
        angles = []
        for hip_idx, knee_idx, ankle_idx in [
            (LEFT_HIP, LEFT_KNEE, LEFT_ANKLE),
            (RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE),
        ]:
            h, k, a = kpts[hip_idx], kpts[knee_idx], kpts[ankle_idx]
            if h.confidence >= conf_thresh and k.confidence >= conf_thresh and a.confidence >= conf_thresh:
                v1 = (h.x - k.x, h.y - k.y)
                v2 = (a.x - k.x, a.y - k.y)
                angle = self._angle_between_vectors(v1, v2)
                angles.append(angle)

        return float(np.mean(angles)) if angles else 180.0

    def _calculate_hip_angle(
        self, kpts: List[Keypoint], conf_thresh: float
    ) -> float:
        """
        Calculate hip flexion angle (shoulder-hip-knee) in degrees.
        Standing straight ~ 180 deg, sitting ~ 90 deg.
        """
        angles = []
        for sh_idx, hip_idx, knee_idx in [
            (LEFT_SHOULDER, LEFT_HIP, LEFT_KNEE),
            (RIGHT_SHOULDER, RIGHT_HIP, RIGHT_KNEE),
        ]:
            s, h, k = kpts[sh_idx], kpts[hip_idx], kpts[knee_idx]
            if s.confidence >= conf_thresh and h.confidence >= conf_thresh and k.confidence >= conf_thresh:
                v1 = (s.x - h.x, s.y - h.y)
                v2 = (k.x - h.x, k.y - h.y)
                angle = self._angle_between_vectors(v1, v2)
                angles.append(angle)

        return float(np.mean(angles)) if angles else 180.0

    def _calculate_shoulder_angle(
        self, kpts: List[Keypoint], conf_thresh: float
    ) -> float:
        """Calculate shoulder angle between left and right shoulders relative to horizontal."""
        ls, rs = kpts[LEFT_SHOULDER], kpts[RIGHT_SHOULDER]
        if ls.confidence >= conf_thresh and rs.confidence >= conf_thresh:
            dx = rs.x - ls.x
            dy = rs.y - ls.y
            angle = math.degrees(abs(math.atan2(dy, dx)))
            return float(angle)
        return 0.0

    def _calculate_hip_ankle_ratio(
        self, kpts: List[Keypoint], vertical_extent: float, conf_thresh: float
    ) -> float:
        """Calculate vertical drop from hip to ankle relative to vertical body extent."""
        if vertical_extent < 1e-4:
            return 0.50
        valid_hips = [kpts[i] for i in (LEFT_HIP, RIGHT_HIP) if kpts[i].confidence >= conf_thresh]
        valid_ankles = [kpts[i] for i in (LEFT_ANKLE, RIGHT_ANKLE) if kpts[i].confidence >= conf_thresh]
        if not valid_hips or not valid_ankles:
            return 0.50
        mid_hy = float(np.mean([h.y for h in valid_hips]))
        mid_ay = float(np.mean([a.y for a in valid_ankles]))
        dy = max(0.0, mid_ay - mid_hy)
        return float(dy / vertical_extent)

    @staticmethod
    def _angle_between_vectors(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
        """Compute the angle between two 2D vectors in degrees."""
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        norm1 = math.hypot(v1[0], v1[1])
        norm2 = math.hypot(v2[0], v2[1])
        if norm1 < 1e-4 or norm2 < 1e-4:
            return 180.0
        cos_theta = max(-1.0, min(1.0, dot / (norm1 * norm2)))
        return float(math.degrees(math.acos(cos_theta)))
