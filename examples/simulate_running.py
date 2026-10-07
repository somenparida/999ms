#!/usr/bin/env python3
"""
Simulation: Running Activity
Simulates Person #1 moving at high velocity and acceleration across the frame.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import generate_running_sequence


def main():
    print("=" * 60)
    print("Warehouse Sentinel - Simulation: RUNNING")
    print("=" * 60)

    engine = BehaviorEngine()
    sequence = generate_running_sequence(
        track_id=1,
        start_time=5.0,
        duration=3.0,
        fps=10.0,
        velocity_px_s=40.0,
    )

    print("Person #1")
    for frame in sequence:
        res = engine.update(
            track_id=frame["track_id"],
            timestamp=frame["timestamp"],
            bbox=frame["bbox"],
            keypoints=frame["keypoints"],
            detection_confidence=frame["detection_confidence"],
        )

        vel = res.motion_features.pixel_velocity if res.motion_features else 0.0
        print(f"{res.timestamp:4.1f}s -> {res.activity.value:<8} {res.confidence:.2f}  (velocity: {vel:4.1f} px/s, duration: {res.activity_duration:.1f}s)")

        if res.event:
            print(f"      [EVENT: {res.event.event_type} | Conf: {res.event.confidence:.2f}]")

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()
