"""Tests for yolodetector.video.io."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import pytest

from yolodetector.video.io import VideoIO, VideoProperties


class TestVideoProperties:
    def test_frozen(self):
        props = VideoProperties(width=1920, height=1080, fps=30.0, total_frames=900)
        with pytest.raises(AttributeError):  # frozen=True
            props.width = 1280

    def test_values(self):
        props = VideoProperties(width=640, height=480, fps=25.0, total_frames=500)
        assert props.width == 640
        assert props.height == 480
        assert props.fps == 25.0
        assert props.total_frames == 500


class TestVideoIOOpenCapture:
    def test_open_success(self):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 900,
        }[prop]

        with patch("yolodetector.video.io.cv2.VideoCapture", return_value=mock_cap):
            vio = VideoIO()
            cap, props = vio.open_capture(Path("test.mp4"))
            assert props.width == 1920
            assert props.fps == 30.0

    def test_open_failure(self):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False

        with patch("yolodetector.video.io.cv2.VideoCapture", return_value=mock_cap):
            vio = VideoIO()
            with pytest.raises(FileNotFoundError, match="Could not open video file"):
                vio.open_capture(Path("nonexistent.mp4"))

    def test_fps_fallback(self):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 640,
            cv2.CAP_PROP_FRAME_HEIGHT: 480,
            cv2.CAP_PROP_FPS: 0.0,  # invalid FPS
            cv2.CAP_PROP_FRAME_COUNT: 100,
        }[prop]

        with patch("yolodetector.video.io.cv2.VideoCapture", return_value=mock_cap):
            vio = VideoIO()
            _, props = vio.open_capture(Path("test.mp4"))
            assert props.fps == 30.0  # fallback


class TestVideoIOCreateWriter:
    def test_create_success(self):
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = True

        with patch("yolodetector.video.io.cv2.VideoWriter", return_value=mock_writer), patch(
            "yolodetector.video.io.cv2.VideoWriter_fourcc", return_value=0x7634706D
        ):
            vio = VideoIO()
            props = VideoProperties(width=1920, height=1080, fps=30.0, total_frames=900)
            writer = vio.create_writer(Path("output.mp4"), props, "mp4v")
            assert writer is mock_writer

    def test_create_failure(self):
        mock_writer = MagicMock()
        mock_writer.isOpened.return_value = False

        with patch("yolodetector.video.io.cv2.VideoWriter", return_value=mock_writer), patch(
            "yolodetector.video.io.cv2.VideoWriter_fourcc", return_value=0x7634706D
        ):
            vio = VideoIO()
            props = VideoProperties(width=1920, height=1080, fps=30.0, total_frames=900)
            with pytest.raises(RuntimeError, match="Could not create video writer"):
                vio.create_writer(Path("bad_output.mp4"), props, "mp4v")
