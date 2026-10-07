#!/usr/bin/env python3
"""
Simulation: Fall Detection Scenario
Simulates Person #1 standing -> rapid downward descent -> impact -> lying motionless -> fall event.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import generate_fall_sequence


def main():
    print("=" * 60)
    print("Warehouse Sentinel - Simulation: FALL DETECTION")
    print("=" * 60)

    engine = BehaviorEngine()
    sequence = generate_fall_sequence(
        track_id=1,
        start_time=10.0,
        fps=10.0,
        standing_y=250.0,
        floor_y=400.0,
    )

    print("Person #1\n")
    fall_events = []

    for frame in sequence:
        res = engine.update(
            track_id=frame["track_id"],
            timestamp=frame["timestamp"],
            bbox=frame["bbox"],
            keypoints=frame["keypoints"],
            detection_confidence=frame["detection_confidence"],
        )

        # Highlight downward kinematic motion during descent
        descent_note = ""
        if res.motion_features and res.motion_features.vertical_velocity > 35.0:
            descent_note = f" (FAST_DOWNWARD_MOVEMENT: {res.motion_features.vertical_velocity:.1f} px/s)"

        print(f"{res.timestamp:4.1f}s  {res.activity.value:<8}  Conf: {res.confidence:.2f}{descent_note}")

        if res.event and "FALL" in str(res.event.event_type):
            fall_events.append(res.event)

    print("\n" + "=" * 40)
    if fall_events:
        evt = fall_events[0]
        print("EVENT DETECTED:")
        print(f"Type:       {evt.event_type}")
        print(f"Timestamp:  {evt.timestamp:.1f}s")
        print(f"Confidence: {evt.confidence:.2f}")
        print(f"Severity:   {evt.severity}")
        print("Reason:")
        for r in evt.reason:
            print(f"  - {r}")
    else:
        print("No fall event detected.")
    print("=" * 40)


if __name__ == "__main__":
    main()
