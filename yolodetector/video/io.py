"""Video input/output utilities."""

import logging
from dataclasses import dataclass
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VideoProperties:
    width: int
    height: int
    fps: float
    total_frames: int


class VideoIO:
    """Handles video capture and writer creation."""

    def open_capture(self, input_path: Path):
        logger.info("Opening video: %s", input_path)
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video file: {input_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps <= 0:
            logger.warning("Invalid FPS (%.1f) for %s, falling back to 30.0", fps, input_path)
            fps = 30.0

        props = VideoProperties(width=width, height=height, fps=fps, total_frames=total_frames)
        logger.debug("Video properties: %dx%d @ %.1f FPS, %d frames", props.width, props.height, props.fps, props.total_frames)
        return cap, props

    def create_writer(self, output_path: Path, props: VideoProperties, codec: str):
        logger.info("Creating writer: %s (codec=%s)", output_path, codec)
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(output_path), fourcc, props.fps, (props.width, props.height))
        if not writer.isOpened():
            raise RuntimeError(f"Could not create video writer: {output_path}")
        return writer
