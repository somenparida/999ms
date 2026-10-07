#!/usr/bin/env python3
"""
Simulation: Sitting Activity
Simulates Person #1 in a stationary seated posture with bent knees.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import generate_sitting_sequence


def main():
    print("=" * 60)
    print("Warehouse Sentinel - Simulation: SITTING")
    print("=" * 60)

    engine = BehaviorEngine()
    sequence = generate_sitting_sequence(
        track_id=1,
        start_time=0.0,
        duration=3.0,
        fps=10.0,
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

        knee_ang = res.pose_features.knee_angle_deg if res.pose_features else 0.0
        print(f"{res.timestamp:4.1f}s -> {res.activity.value:<8} {res.confidence:.2f}  (knee angle: {knee_ang:5.1f} deg, duration: {res.activity_duration:.1f}s)")

        if res.event:
            print(f"      [EVENT: {res.event.event_type} | Conf: {res.event.confidence:.2f}]")

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()
