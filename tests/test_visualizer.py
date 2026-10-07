"""
Tests for Debug & Visualization Module.
"""

import numpy as np
import pytest
from behavior.visualizer import BehaviorVisualizer
from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import generate_walking_sequence


def test_visualizer_renders_frame():
    engine = BehaviorEngine()
    visualizer = BehaviorVisualizer()

    sequence = generate_walking_sequence(track_id=1, duration=0.5, fps=10.0)
    frame_canvas = np.zeros((480, 640, 3), dtype=np.uint8)

    for item in sequence:
        res = engine.update(
            item["track_id"],
            item["timestamp"],
            item["bbox"],
            item["keypoints"],
            item["detection_confidence"],
        )
        rendered = visualizer.draw_result(
            frame=frame_canvas,
            result=res,
            bbox_coords=item["bbox"],
            keypoints=item["keypoints"],
        )
        assert rendered is not None
        assert rendered.shape == (480, 640, 3)
        assert rendered.dtype == np.uint8
