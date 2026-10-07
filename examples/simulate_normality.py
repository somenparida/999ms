#!/usr/bin/env python3
"""
Warehouse Sentinel - Normal vs Abnormal Behavior Simulation
Demonstrates the 5 core scenarios requested:
  1. Person #1: WALKING -> NORMAL
  2. Person #2: BENDING (short duration) -> NORMAL
  3. Person #3: BENDING for 42 seconds -> POTENTIALLY UNUSUAL
  4. Person #4: FALLING -> ABNORMAL
  5. Person #4: LYING after fall -> ABNORMAL
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from behavior.normality import classify_behavior
from behavior.schemas import ActivityType, BehaviorStatus

STATUS_ICONS = {
    BehaviorStatus.NORMAL: "[OK] NORMAL",
    BehaviorStatus.POTENTIALLY_UNUSUAL: "[WARN] POTENTIALLY_UNUSUAL",
    BehaviorStatus.ABNORMAL: "[ALERT] ABNORMAL",
    BehaviorStatus.UNKNOWN: "[?] UNKNOWN",
}


def print_case(title: str, activity: ActivityType, duration: float, prev_act=None, has_fallen=False):
    res = classify_behavior(activity, duration=duration, previous_activity=prev_act, has_fallen=has_fallen)
    icon_str = STATUS_ICONS.get(res.status, str(res.status))

    print(f"\n{title}")
    print(f"  Activity:  {activity.value} ({duration:.1f}s)")
    print(f"  Status:    {icon_str}")
    print(f"  Severity:  {res.severity.value}")
    if res.reason:
        print(f"  Reason:    {res.reason}")

    out_dict = {
        "activity": activity.value,
        "status": res.status.value,
        "severity": res.severity.value,
        "reason": res.reason,
    }
    print(f"  Structured: {json.dumps(out_dict)}")


def main():
    print("=" * 65)
    print("Warehouse Sentinel: Normal vs. Abnormal Behavior Intelligence")
    print("=" * 65)

    # 1. Walking (normal)
    print_case("Person #1: Active warehouse transit", ActivityType.WALKING, duration=8.5)

    # 2. Bending (short duration - normal)
    print_case("Person #2: Brief inspection or lift", ActivityType.BENDING, duration=4.2)

    # 3. Bending for 42s (prolonged - potentially unusual ergonomic risk)
    print_case("Person #3: Prolonged bending at lower shelf", ActivityType.BENDING, duration=42.0)

    # 4. Crouching for 35s (prolonged - potentially unusual)
    print_case("Person #3b: Prolonged crouching", ActivityType.CROUCHING, duration=35.0)

    # 5. Falling (abnormal)
    print_case("Person #4: Sudden slip-and-fall incident", ActivityType.FALLING, duration=1.2)

    # 6. Lying after fall (abnormal)
    print_case(
        "Person #4: Lying motionless on floor after fall",
        ActivityType.LYING,
        duration=15.0,
        prev_act=ActivityType.FALLING,
        has_fallen=True,
    )

    # 7. Intentional resting lying (short duration without fall)
    print_case("Person #5: Brief rest in lounge area", ActivityType.LYING, duration=8.0, has_fallen=False)

    print("\n" + "=" * 65)
    print("Simulation complete.")


if __name__ == "__main__":
    main()
