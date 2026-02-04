"""Tests for yolodetector.config."""

from pathlib import Path

import pytest

from yolodetector.config import AnnotationConfig, ApplicationConfig, DetectionConfig, VideoConfig


class TestDetectionConfig:
    def test_defaults(self):
        cfg = DetectionConfig()
        assert cfg.model_name == "yolo26x.pt"
        assert cfg.device == "mps"
        assert cfg.confidence_threshold == 0.25
        assert cfg.iou_threshold == 0.45
        assert cfg.imgsz is None

    def test_valid_thresholds(self):
        cfg = DetectionConfig(confidence_threshold=0.0, iou_threshold=1.0)
        assert cfg.confidence_threshold == 0.0
        assert cfg.iou_threshold == 1.0

    def test_invalid_confidence_low(self):
        with pytest.raises(ValueError, match="Confidence threshold"):
            DetectionConfig(confidence_threshold=-0.1)

    def test_invalid_confidence_high(self):
        with pytest.raises(ValueError, match="Confidence threshold"):
            DetectionConfig(confidence_threshold=1.1)

    def test_invalid_iou_low(self):
        with pytest.raises(ValueError, match="IOU threshold"):
            DetectionConfig(iou_threshold=-0.01)

    def test_invalid_iou_high(self):
        with pytest.raises(ValueError, match="IOU threshold"):
            DetectionConfig(iou_threshold=1.01)


class TestVideoConfig:
    def test_string_path_coercion(self, tmp_path):
        cfg = VideoConfig(input_dir=str(tmp_path), output_dir=str(tmp_path / "out"), file_prefix="test")
        assert isinstance(cfg.input_dir, Path)
        assert isinstance(cfg.output_dir, Path)

    def test_output_dir_created(self, tmp_path):
        out = tmp_path / "nested" / "output"
        cfg = VideoConfig(input_dir=tmp_path, output_dir=out, file_prefix="test")
        assert out.exists()

    def test_get_video_files_main_found(self, tmp_path):
        video = tmp_path / "clip.mp4"
        video.touch()
        cfg = VideoConfig(input_dir=tmp_path, output_dir=tmp_path / "out", file_prefix="clip")
        files = cfg.get_video_files()
        assert len(files) == 1
        assert files[0] == video

    def test_get_video_files_main_missing(self, tmp_path):
        cfg = VideoConfig(input_dir=tmp_path, output_dir=tmp_path / "out", file_prefix="missing")
        with pytest.raises(FileNotFoundError, match="Main video file not found"):
            cfg.get_video_files()

    def test_get_video_files_with_cameras(self, tmp_path):
        for suffix in ["", "_FACE", "_TOP"]:
            (tmp_path / f"clip{suffix}.mp4").touch()
        cfg = VideoConfig(input_dir=tmp_path, output_dir=tmp_path / "out", file_prefix="clip", include_cameras=True)
        files = cfg.get_video_files()
        assert len(files) == 3

    def test_get_video_files_cameras_optional_missing(self, tmp_path):
        (tmp_path / "clip.mp4").touch()  # main exists, cameras do not
        cfg = VideoConfig(input_dir=tmp_path, output_dir=tmp_path / "out", file_prefix="clip", include_cameras=True)
        files = cfg.get_video_files()
        assert len(files) == 1  # only main returned


class TestAnnotationConfig:
    def test_default_critical_classes(self):
        cfg = AnnotationConfig()
        assert cfg.is_critical("cell phone")
        assert not cfg.is_critical("person")

    def test_get_color_wraps(self):
        cfg = AnnotationConfig()
        palette_size = len(cfg.color_palette)
        assert cfg.get_color(0) == cfg.get_color(palette_size)
        assert cfg.get_color(1) == cfg.get_color(palette_size + 1)

    def test_get_color_deterministic(self):
        cfg = AnnotationConfig()
        assert cfg.get_color(5) == cfg.get_color(5)


class TestApplicationConfig:
    def test_create_default_model(self):
        cfg = ApplicationConfig.create_default()
        assert cfg.detection.model_name == "yolo26x.pt"

    def test_create_default_custom_model(self):
        cfg = ApplicationConfig.create_default(model_name="yolov8x.pt")
        assert cfg.detection.model_name == "yolov8x.pt"

    def test_create_default_paths(self):
        cfg = ApplicationConfig.create_default(input_dir="/tmp/test", file_prefix="vid")
        assert cfg.video.input_dir == Path("/tmp/test")
        assert cfg.video.file_prefix == "vid"
