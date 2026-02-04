#!/usr/bin/env python3
"""
YOLO DETECTOR - Multi-model YOLO Testing Framework
Test and compare multiple YOLO versions with critical object marking.

Copyright (C) 2026 Kinn Coelho Juliao <kinncj@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Note: Standard YOLO (COCO dataset) includes 'cell phone' but NOT 'glasses'.
To detect glasses, upgrade to ultralytics>=8.1.0 and use YOLO-World.
"""

import argparse
import logging
import time
from pathlib import Path

from tqdm import tqdm

from yolodetector.annotation.renderer import FrameAnnotator
from yolodetector.config import (
    AnnotationConfig,
    ApplicationConfig,
    DetectionConfig,
    VideoConfig,
)
from yolodetector.models.detector import YoloDetector
from yolodetector.reporting.summary import ReportAggregator, VideoReport
from yolodetector.video.io import VideoIO


DEFAULT_APP = ApplicationConfig.create_default()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="YOLO Object Detection with Critical Object Marking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process only main video (default)
  python main.py

  # Process all camera angles (main, face, top)
  python main.py --all

  # Same as above
  python main.py --include-cameras
        '''
    )
    parser.add_argument(
        "--all", "--include-cameras",
        dest="include_cameras",
        action="store_true",
        help="Include FACE and TOP camera videos (default: main video only)",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_APP.video.input_dir,
        help=f"Input directory (default: {DEFAULT_APP.video.input_dir})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_APP.video.output_dir,
        help=f"Output directory (default: {DEFAULT_APP.video.output_dir})",
    )
    parser.add_argument(
        "--prefix",
        default=DEFAULT_APP.video.file_prefix,
        help=f"File prefix to search for (default: {DEFAULT_APP.video.file_prefix})",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=DEFAULT_APP.detection.confidence_threshold,
        help=f"Confidence threshold (default: {DEFAULT_APP.detection.confidence_threshold})",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=DEFAULT_APP.detection.iou_threshold,
        help=f"IoU threshold (default: {DEFAULT_APP.detection.iou_threshold})",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=DEFAULT_APP.detection.imgsz,
        help="Inference image size (default: None)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_APP.detection.model_name,
        help=f"YOLO model to use (default: {DEFAULT_APP.detection.model_name})",
    )
    parser.add_argument(
        "--device",
        default=DEFAULT_APP.detection.device,
        help=f"Device to use (default: {DEFAULT_APP.detection.device})",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging verbosity (default: WARNING)",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Path to write JSON report file",
    )

    return parser.parse_args()


def build_config(args: argparse.Namespace) -> ApplicationConfig:
    """Build an ApplicationConfig from CLI args."""
    output_dir = args.output_dir
    if args.input_dir != DEFAULT_APP.video.input_dir and args.output_dir == DEFAULT_APP.video.output_dir:
        output_dir = args.input_dir / "output"

    detection = DetectionConfig(
        model_name=args.model,
        device=args.device,
        confidence_threshold=args.conf,
        iou_threshold=args.iou,
        imgsz=args.imgsz,
    )
    video = VideoConfig(
        input_dir=args.input_dir,
        output_dir=output_dir,
        file_prefix=args.prefix,
        include_cameras=args.include_cameras,
    )
    annotation = AnnotationConfig()

    return ApplicationConfig(detection=detection, video=video, annotation=annotation)


def process_video(detector: YoloDetector, annotator: FrameAnnotator, video_io: VideoIO,
                  input_path: Path, output_path: Path, app_config: ApplicationConfig):
    print(f"\n{'=' * 70}")
    print(f"Processing: {input_path.name}")
    print(f"{'=' * 70}")

    cap, props = video_io.open_capture(input_path)
    print(f"Resolution: {props.width}x{props.height}")
    print(f"FPS: {props.fps:.2f}")
    print(f"Total frames: {props.total_frames}")

    writer = video_io.create_writer(output_path, props, app_config.video.codec)

    detections = {}
    criticals = []
    start_time = time.time()

    progress_total = props.total_frames if props.total_frames > 0 else None
    with tqdm(total=progress_total, desc="Processing", unit="frame") as pbar:
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = detector.predict(
                frame,
                device=app_config.detection.device,
                conf=app_config.detection.confidence_threshold,
                iou=app_config.detection.iou_threshold,
                imgsz=app_config.detection.imgsz,
            )

            annotated_frame, det_summary, critical = annotator.annotate_frame(frame, results)

            for cls_name, count in det_summary.items():
                detections[cls_name] = detections.get(cls_name, 0) + count

            for crit_obj in critical:
                criticals.append((frame_idx, *crit_obj))

            writer.write(annotated_frame)
            frame_idx += 1
            pbar.update(1)

    cap.release()
    writer.release()

    elapsed = time.time() - start_time
    fps_processed = props.total_frames / elapsed if elapsed > 0 else 0
    print(f"\nCompleted in {elapsed:.1f}s ({fps_processed:.2f} FPS)")
    print(f"Output saved to: {output_path}")

    return detections, criticals


def main():
    """Main entry point."""
    args = parse_args()
    model_names = [name.strip() for name in args.model.split(",") if name.strip()]
    if not model_names:
        print("ERROR: No models specified.")
        return 1

    app_config = build_config(args)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 70)
    print("YOLO Object Detection with Critical Object Marking")
    print("=" * 70)
    print(f"Models: {', '.join(model_names)}")
    print(f"Device: {app_config.detection.device}")
    print(f"Confidence threshold: {app_config.detection.confidence_threshold}")
    print(f"IoU threshold: {app_config.detection.iou_threshold}")
    print(f"Image size: {app_config.detection.imgsz}")
    print(f"Critical classes: {list(app_config.annotation.critical_classes.keys())}")

    if "glasses" in str(app_config.annotation.critical_classes).lower():
        print("\n⚠️  NOTE: 'glasses' and 'sunglasses' require YOLO-World (ultralytics>=8.1.0)")
    else:
        print("\n⚠️  NOTE: Standard YOLO (COCO) does NOT include 'glasses' class.")
        print("    Only 'cell phone' can be detected as critical.")
        print("    To detect glasses, upgrade: pip install ultralytics>=8.1.0")
    print(f"\nInput directory: {app_config.video.input_dir}")
    print(f"Output directory: {app_config.video.output_dir}")

    try:
        input_files = app_config.video.get_video_files()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    mode_label = "ALL camera angles (main, face, top)" if app_config.video.include_cameras else "MAIN video only"
    print(f"\nMode: Processing {mode_label} (use --all to include cameras)")

    print(f"\nFound {len(input_files)} video file(s) to process:")
    for f in input_files:
        print(f"  - {f.name}")

    video_io = VideoIO()
    annotator = FrameAnnotator(app_config.annotation)

    total_start = time.time()
    for model_name in model_names:
        print(f"\nLoading {model_name}...")
        try:
            detector = YoloDetector(model_name)
            print("Model loaded successfully")
            print(f"Classes available: {len(detector.names)}")
        except Exception as e:
            print(f"ERROR: Failed to load model: {e}")
            return 1

        model_config = ApplicationConfig(
            detection=DetectionConfig(
                model_name=model_name,
                device=app_config.detection.device,
                confidence_threshold=app_config.detection.confidence_threshold,
                iou_threshold=app_config.detection.iou_threshold,
                imgsz=app_config.detection.imgsz,
            ),
            video=app_config.video,
            annotation=app_config.annotation,
        )

        reporter = ReportAggregator(model_config.annotation.critical_classes)

        for input_path in input_files:
            model_tag = Path(model_name).stem
            output_name = f"{input_path.stem}_{model_tag}_detected.mp4"
            output_path = model_config.video.output_dir / output_name

            detections, criticals = process_video(
                detector,
                annotator,
                video_io,
                input_path,
                output_path,
                model_config,
            )

            report = VideoReport(detections=detections, criticals=criticals, output_path=str(output_path))
            reporter.record_video(input_path.name, report)
            reporter.print_video_summary(report)

        total_elapsed = time.time() - total_start
        reporter.print_final_summary(total_elapsed)

        if args.report_json:
            reporter.export_json(str(args.report_json), total_elapsed)

    return 0


if __name__ == "__main__":
    exit(main())
