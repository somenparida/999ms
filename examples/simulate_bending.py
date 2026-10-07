#!/usr/bin/env python3
"""
Simulation: Bending / Stooping Activity
Simulates Person #1 bending forward at the waist with straight legs.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import generate_bending_sequence


def main():
    print("=" * 60)
    print("Warehouse Sentinel - Simulation: BENDING")
    print("=" * 60)

    engine = BehaviorEngine()
    sequence = generate_bending_sequence(
        track_id=1,
        start_time=0.0,
        duration=2.5,
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

        torso_ang = res.pose_features.torso_angle_deg if res.pose_features else 0.0
        knee_ang = res.pose_features.knee_angle_deg if res.pose_features else 0.0
        print(
            f"{res.timestamp:4.1f}s -> {res.activity.value:<10} {res.confidence:.2f}  "
            f"(torso angle: {torso_ang:5.1f} deg, knee angle: {knee_ang:5.1f} deg, duration: {res.activity_duration:.1f}s)"
        )

        if res.event:
            print(f"      [EVENT: {res.event.event_type} | Conf: {res.event.confidence:.2f}]")

    print("\nSimulation complete.")


if __name__ == "__main__":
    main()
