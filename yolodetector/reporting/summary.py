"""Detection reporting utilities."""

from collections import defaultdict
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class VideoReport:
    detections: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    criticals: List[Tuple[int, str, float, tuple]] = field(default_factory=list)
    output_path: str = ""


class ReportAggregator:
    """Aggregates and prints detection summaries."""

    def __init__(self, critical_classes: Dict[str, str]):
        self._critical_classes = critical_classes
        self._videos: Dict[str, VideoReport] = {}

    def record_video(self, video_name: str, report: VideoReport):
        self._videos[video_name] = report

    def print_video_summary(self, report: VideoReport):
        total = sum(report.detections.values())
        logger.info("Video summary: %d total detections, %d critical instances", total, len(report.criticals))
        print(f"Total detections: {total}")

        if report.detections:
            print("\nDetection breakdown:")
            for cls_name, count in sorted(report.detections.items(), key=lambda x: x[1], reverse=True):
                marker = "[CRITICAL]" if cls_name in self._critical_classes else ""
                print(f"  {cls_name:20s}: {count:6d} {marker}")

        if report.criticals:
            print(f"\n{'*' * 70}")
            print(f"*** CRITICAL OBJECTS DETECTED: {len(report.criticals)} instances ***")
            print(f"{'*' * 70}")
            for frame_idx, cls_name, conf, box in report.criticals:
                print(f"  Frame {frame_idx:6d}: {cls_name:15s} ({conf:.0%}) at {box}")

    def print_final_summary(self, total_time: float):
        total_criticals = sum(len(v.criticals) for v in self._videos.values())
        logger.info("Final summary: %d videos, %.1fs, %d total criticals", len(self._videos), total_time, total_criticals)

        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total time: {total_time:.1f}s")
        print(f"Videos processed: {len(self._videos)}")

        if total_criticals > 0:
            print(f"\n{'!' * 70}")
            print(f"TOTAL CRITICAL OBJECTS ACROSS ALL VIDEOS: {total_criticals}")
            print(f"{'!' * 70}")

        print("\nOutput files:")
        for report in self._videos.values():
            print(f"  {Path(report.output_path).name}")

    def export_json(self, output_path: str, total_time: float):
        """Export structured report to JSON file."""
        data = {
            "total_time_seconds": round(total_time, 2),
            "videos_processed": len(self._videos),
            "total_criticals": sum(len(v.criticals) for v in self._videos.values()),
            "videos": {}
        }
        for video_name, report in self._videos.items():
            data["videos"][video_name] = {
                "detections": dict(report.detections),
                "total_detections": sum(report.detections.values()),
                "criticals": [
                    {
                        "frame": c[0],
                        "class": c[1],
                        "confidence": round(c[2], 4),
                        "bbox": list(c[3]),
                    }
                    for c in report.criticals
                ],
                "output_path": report.output_path,
            }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Report exported to: %s", path)
        print(f"Report exported to: {path}")
