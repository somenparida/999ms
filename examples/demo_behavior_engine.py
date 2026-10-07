#!/usr/bin/env python3
"""
Warehouse Sentinel - Comprehensive Behavior Intelligence Demo
Demonstrates concurrent multi-person behavioral analysis, state transitions,
structured event outputs, and optional visual frame generation.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.behavior_engine import BehaviorEngine
from data.synthetic.generator import (
    generate_standing_sequence,
    generate_walking_sequence,
    generate_running_sequence,
    generate_fall_sequence,
)


def main():
    print("=" * 70)
    print("Warehouse Sentinel - Behavior Intelligence Multi-Track Demonstration")
    print("=" * 70)

    engine = BehaviorEngine()

    print("\n[SCENARIO 1] Three concurrent subjects in the warehouse:")
    print("  Track 1: Worker walking towards aisle A")
    print("  Track 2: Supervisor standing at workstation")
    print("  Track 3: Forklift spotter running to alert team\n")

    t1_frames = generate_walking_sequence(track_id=1, start_time=0.0, duration=2.0, velocity_px_s=14.0)
    t2_frames = generate_standing_sequence(track_id=2, start_time=0.0, duration=2.0)
    t3_frames = generate_running_sequence(track_id=3, start_time=0.0, duration=2.0, velocity_px_s=38.0)

    # Interleave and process
    for f1, f2, f3 in zip(t1_frames, t2_frames, t3_frames):
        r1 = engine.update(f1["track_id"], f1["timestamp"], f1["bbox"], f1["keypoints"], f1["detection_confidence"])
        r2 = engine.update(f2["track_id"], f2["timestamp"], f2["bbox"], f2["keypoints"], f2["detection_confidence"])
        r3 = engine.update(f3["track_id"], f3["timestamp"], f3["bbox"], f3["keypoints"], f3["detection_confidence"])

        print(
            f"[{r1.timestamp:4.1f}s] "
            f"T1: {r1.activity.value:<8} ({r1.confidence:.2f}) | "
            f"T2: {r2.activity.value:<8} ({r2.confidence:.2f}) | "
            f"T3: {r3.activity.value:<8} ({r3.confidence:.2f})"
        )

    print("\n" + "-" * 70)
    print("[SCENARIO 2] Worker (Track 1) experiences a slip & fall incident:")
    print("-" * 70)

    engine.reset()
    fall_seq = generate_fall_sequence(track_id=1, start_time=10.0, fps=10.0)

    last_res = None
    for frame in fall_seq:
        res = engine.update(
            frame["track_id"],
            frame["timestamp"],
            frame["bbox"],
            frame["keypoints"],
            frame["detection_confidence"],
        )
        if res.event and "FALL" in str(res.event.event_type):
            last_res = res
            print(f"\n>>> CRITICAL ALERT at {res.timestamp:.1f}s:")
            print(json.dumps(res.to_dict(), indent=2))
            break

    print("\n" + "=" * 70)
    print("Demonstration successfully finished.")
    print("=" * 70)


if __name__ == "__main__":
    main()
