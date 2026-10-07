"""Warehouse Sentinel - Integrated Video Intelligence Runner.

Combines Member 1 (YOLO11 + ByteTrack) with Member 2 (Behavior Intelligence)
to process video feeds, detect persons, track trajectories, analyze behaviors,
flag safety hazards, and export rich diagnostic video & telemetry.

Usage:
    python run_sentinel.py --input autonomous-vision/data/input/multi_person.mp4
    python run_sentinel.py --input autonomous-vision/data/input/videoplayback.mp4 --conf 0.3
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add project root and autonomous-vision to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent
_VISION_ROOT = _PROJECT_ROOT / "autonomous-vision"

for _p in [str(_PROJECT_ROOT), str(_VISION_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pipeline.sentinel_pipeline import SentinelPipeline


def main() -> None:
    """CLI entry point for running the integrated Warehouse Sentinel pipeline."""
    parser = argparse.ArgumentParser(
        description="Warehouse Sentinel - Real-Time Behavior Intelligence & Tracking System"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=str,
        help="Path to input video file (e.g. data/input/multi_person.mp4)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to output annotated MP4 video (default: output/<stem>_sentinel.mp4)",
    )
    parser.add_argument(
        "--json-output",
        "-j",
        type=str,
        default=None,
        help="Path to telemetry JSON export (default: output/<stem>_sentinel.json)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="autonomous-vision/models/yolo11n.pt",
        help="Path to YOLO model weights (default: autonomous-vision/models/yolo11n.pt)",
    )
    parser.add_argument(
        "--behavior-config",
        type=str,
        default="configs/behavior.yaml",
        help="Path to behavior configuration YAML (default: configs/behavior.yaml)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detection confidence threshold (default: 0.25)",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="NMS IoU threshold (default: 0.45)",
    )
    parser.add_argument(
        "--tracker-config",
        type=str,
        default="bytetrack.yaml",
        help="ByteTrack configuration file (default: bytetrack.yaml)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Computation device ('cpu', 'cuda', etc.)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("  WAREHOUSE SENTINEL — INTEGRATED BEHAVIOR & TRACKING INTELLIGENCE")
    print("  Member 1 (YOLO11 + ByteTrack) + Member 2 (Behavior Engine)")
    print("=" * 70)

    try:
        pipeline = SentinelPipeline(
            model_path=args.model,
            behavior_config=args.behavior_config,
            conf_threshold=args.conf,
            iou_threshold=args.iou,
            tracker_config=args.tracker_config,
            device=args.device,
        )

        def print_progress(cur: int, total: int) -> None:
            if total > 0 and (cur % 5 == 0 or cur == total):
                percent = (cur / total) * 100
                sys.stdout.write(f"\r[Processing] Frame: {cur}/{total} ({percent:.1f}%)")
                sys.stdout.flush()

        print(f"Input Video     : {args.input}")
        print(f"YOLO Model      : {pipeline.model_path}")
        print(f"Tracker Config  : {args.tracker_config}")
        print(f"Behavior Config : {pipeline.behavior_config}")
        print(f"Confidence      : {args.conf}")
        print("-" * 70)

        summary = pipeline.process_video(
            input_path=args.input,
            output_video_path=args.output,
            json_output_path=args.json_output,
            progress_callback=print_progress,
        )

        print("\n" + "=" * 70)
        print("  PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Annotated Video      : {summary['output_video_path']}")
        print(f"JSON Telemetry       : {summary['json_output_path']}")
        print(f"Resolution & FPS     : {summary['width']}x{summary['height']} @ {summary['fps']:.2f} FPS")
        print(f"Frames Processed     : {summary['total_frames_processed']}")
        print(f"Unique Persons       : {summary['unique_person_count']} (IDs: {summary['unique_track_ids']})")
        print(f"Total Track Records  : {summary['total_tracking_records']}")
        print(f"Total Safety Events  : {summary['total_safety_events']}")
        print(f"Elapsed Time         : {summary['elapsed_seconds']}s ({summary['processing_fps']:.1f} FPS)")

        print("-" * 70)
        print("ACTIVITY DISTRIBUTION:")
        for act, cnt in sorted(summary["activity_distribution"].items(), key=lambda x: -x[1]):
            print(f"  • {act:<20}: {cnt:>4} occurrences")

        print("-" * 70)
        print("BEHAVIOR STATUS BREAKDOWN:")
        for stat, cnt in summary["status_distribution"].items():
            print(f"  • {stat:<20}: {cnt:>4} occurrences")

        if summary["events"]:
            print("-" * 70)
            print("SAFETY HAZARDS & ALERTS:")
            for ev in summary["events"]:
                reasons = ", ".join(ev.get("reason", [])) if ev.get("reason") else "No additional details"
                print(f"  ⚠️  [Track {ev.get('track_id')}] {ev.get('type')} ({ev.get('severity')}) at {ev.get('timestamp'):.2f}s: {reasons}")

        print("=" * 70)

    except Exception as exc:
        print(f"\n[ERROR] Pipeline execution failed: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
