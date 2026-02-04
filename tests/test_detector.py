"""Tests for yolodetector.models.detector."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from yolodetector.models.detector import YoloDetector


class TestResolveModelPath:
    """Test _resolve_model_path static method directly (no model loading)."""

    def test_appends_pt_extension(self):
        with patch.object(Path, 'exists', return_value=False), \
             patch('yolodetector.models.detector.attempt_download', None), \
             patch.object(YoloDetector, '_download_from_ultralytics_assets', return_value=None):
            result = YoloDetector._resolve_model_path("yolo26x")
            assert result == "yolo26x.pt"  # fallback returns normalized_name

    def test_local_file_exact_match(self, tmp_path):
        model_file = tmp_path / "custom.pt"
        model_file.touch()
        result = YoloDetector._resolve_model_path(str(model_file))
        assert result == str(model_file)

    def test_attempt_download_called(self):
        mock_download = MagicMock(return_value="downloaded.pt")
        with patch.object(Path, 'exists', return_value=False), \
             patch('yolodetector.models.detector.attempt_download', mock_download):
            result = YoloDetector._resolve_model_path("yolo26x.pt")
            assert result == "downloaded.pt"
            mock_download.assert_called_once_with("yolo26x.pt")

    def test_attempt_download_fallback_on_failure(self):
        mock_download = MagicMock(side_effect=Exception("download error"))
        with patch.object(Path, 'exists', return_value=False), \
             patch('yolodetector.models.detector.attempt_download', mock_download), \
             patch.object(YoloDetector, '_download_from_ultralytics_assets', return_value=None):
            result = YoloDetector._resolve_model_path("yolo26x.pt")
            assert result == "yolo26x.pt"  # falls through to normalized_name


class TestPredict:
    def test_predict_without_imgsz(self):
        with patch('yolodetector.models.detector.YOLO') as MockYOLO:
            mock_model = MagicMock()
            mock_model.names = {0: "person"}
            MockYOLO.return_value = mock_model
            with patch.object(YoloDetector, '_resolve_model_path', return_value="fake.pt"):
                detector = YoloDetector("fake.pt")
                frame = MagicMock()
                detector.predict(frame, device="cpu", conf=0.5, iou=0.4, imgsz=None)
                mock_model.assert_called_once()
                call_kwargs = mock_model.call_args[1]
                assert "imgsz" not in call_kwargs
                assert call_kwargs["conf"] == 0.5

    def test_predict_with_imgsz(self):
        with patch('yolodetector.models.detector.YOLO') as MockYOLO:
            mock_model = MagicMock()
            mock_model.names = {0: "person"}
            MockYOLO.return_value = mock_model
            with patch.object(YoloDetector, '_resolve_model_path', return_value="fake.pt"):
                detector = YoloDetector("fake.pt")
                frame = MagicMock()
                detector.predict(frame, device="cpu", conf=0.5, iou=0.4, imgsz=640)
                call_kwargs = mock_model.call_args[1]
                assert call_kwargs["imgsz"] == 640
