"""Configuration management following Single Responsibility Principle."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DetectionConfig:
    """Configuration for object detection.

    Follows Single Responsibility: Only manages detection parameters.
    """
    model_name: str = "yolo26x.pt"
    device: str = "mps"
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45
    imgsz: Optional[int] = None

    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0 and 1")
        if not 0.0 <= self.iou_threshold <= 1.0:
            raise ValueError("IOU threshold must be between 0 and 1")


@dataclass
class VideoConfig:
    """Configuration for video processing.

    Follows Single Responsibility: Only manages video I/O parameters.
    """
    input_dir: Path
    output_dir: Path
    file_prefix: str
    codec: str = "mp4v"
    include_cameras: bool = False

    def __post_init__(self):
        """Convert string paths to Path objects."""
        if isinstance(self.input_dir, str):
            self.input_dir = Path(self.input_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_video_files(self) -> List[Path]:
        """Discover video files based on configuration."""
        suffixes = ['', '_FACE', '_TOP'] if self.include_cameras else ['']
        files = []

        for suffix in suffixes:
            path = self.input_dir / f"{self.file_prefix}{suffix}.mp4"
            if path.exists():
                files.append(path)
            elif suffix == '':  # Main file is required
                raise FileNotFoundError(f"Main video file not found: {path}")

        return files


@dataclass
class AnnotationConfig:
    """Configuration for annotation rendering.

    Follows Single Responsibility: Only manages visual styling.
    """
    critical_classes: Dict[str, str] = field(default_factory=lambda: {
        "cell phone": "PHONE",
    })

    critical_color_bgr: tuple = (0, 0, 255)  # Red
    critical_icon_color_bgr: tuple = (0, 255, 255)  # Yellow
    critical_thickness: int = 4
    normal_thickness: int = 2

    # Color palette for non-critical objects (BGR format)
    color_palette: List[tuple] = field(default_factory=lambda: [
        (255, 56, 56), (255, 157, 151), (255, 112, 31), (255, 178, 29),
        (207, 210, 49), (72, 249, 10), (146, 204, 23), (61, 219, 134),
        (26, 147, 52), (0, 212, 187), (44, 153, 168), (0, 194, 255),
        (52, 69, 147), (100, 115, 255), (0, 24, 236), (132, 56, 255),
        (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199)
    ])

    def get_color(self, class_id: int) -> tuple:
        """Get a consistent color for a class ID."""
        return self.color_palette[class_id % len(self.color_palette)]

    def is_critical(self, class_name: str) -> bool:
        """Check if a class is marked as critical."""
        return class_name in self.critical_classes


@dataclass
class ApplicationConfig:
    """Complete application configuration.

    Follows Dependency Inversion: High-level config depends on abstractions.
    """
    detection: DetectionConfig
    video: VideoConfig
    annotation: AnnotationConfig

    @classmethod
    def create_default(cls,
                      input_dir: str = ".",
                      file_prefix: str = "dummy",
                      model_name: str = "yolo26x.pt") -> "ApplicationConfig":
        """Factory method to create default configuration."""
        input_path = Path(input_dir)
        return cls(
            detection=DetectionConfig(model_name=model_name),
            video=VideoConfig(
                input_dir=input_path,
                output_dir=input_path / "output",
                file_prefix=file_prefix
            ),
            annotation=AnnotationConfig()
        )
