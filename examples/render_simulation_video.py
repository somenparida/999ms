#!/usr/bin/env python3
"""
Warehouse Sentinel - Visual Simulation Video Generator
Generates a video file (MP4) with realistic rendered bounding boxes,
skeletons, velocity meters, and fall alert banners.
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from behavior.visualizer import BehaviorVisualizer
from data.synthetic.generator import (
    generate_walking_sequence,
    generate_running_sequence,
    generate_fall_sequence,
)


def main():
    print("=" * 60)
    print("Warehouse Sentinel - Generating Simulation Video")
    print("=" * 60)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    video_path = output_dir / "warehouse_simulation.mp4"

    width, height = 800, 600
    fps = 15.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

    engine = BehaviorEngine()
    visualizer = BehaviorVisualizer()

    # Generate a story:
    # 1. Person 1 walks (0.0s - 2.5s)
    # 2. Person 1 runs (2.5s - 5.0s)
    # 3. Person 1 experiences a slip and fall (5.0s - 9.0s)
    seq_walk = generate_walking_sequence(track_id=1, start_time=0.0, duration=2.5, fps=fps, velocity_px_s=18.0)
    seq_run = generate_running_sequence(track_id=1, start_time=2.5, duration=2.5, fps=fps, start_x=145.0, velocity_px_s=42.0)
    seq_fall = generate_fall_sequence(track_id=1, start_time=5.0, fps=fps, center_x=350.0, standing_y=280.0, floor_y=460.0)

    full_sequence = seq_walk + seq_run + seq_fall
    print(f"Rendering {len(full_sequence)} simulation frames to {video_path}...")

    for frame_data in full_sequence:
        # Create dark warehouse camera floor canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        # Background floor grid
        for y in range(0, height, 50):
            cv2.line(canvas, (0, y), (width, y), (25, 25, 25), 1)
        for x in range(0, width, 50):
            cv2.line(canvas, (x, 0), (x, height), (25, 25, 25), 1)

        # Camera watermark
        cv2.putText(
            canvas,
            f"CAM 04 - AISLE B [SYNTHETIC TEST]  T: {frame_data['timestamp']:.2f}s",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (180, 180, 180),
            1,
            cv2.LINE_AA,
        )

        res = engine.update(
            track_id=frame_data["track_id"],
            timestamp=frame_data["timestamp"],
            bbox=frame_data["bbox"],
            keypoints=frame_data["keypoints"],
            detection_confidence=frame_data["detection_confidence"],
        )

        rendered = visualizer.draw_result(
            frame=canvas,
            result=res,
            bbox_coords=frame_data["bbox"],
            keypoints=frame_data["keypoints"],
        )

        writer.write(rendered)

    writer.release()
    print(f"Video successfully generated: {video_path.resolve()}")
    print("You can open this MP4 file to inspect the behavior detection visually!")


if __name__ == "__main__":
    main()
