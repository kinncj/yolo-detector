"""Shared test fixtures."""

import pytest
import numpy as np
from unittest.mock import MagicMock
from yolodetector.config import AnnotationConfig, DetectionConfig, VideoConfig, ApplicationConfig


@pytest.fixture
def annotation_config():
    return AnnotationConfig()


@pytest.fixture
def detection_config():
    return DetectionConfig(model_name="yolo26x.pt")


@pytest.fixture
def sample_frame():
    """640x480 BGR frame (black)."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def mock_yolo_result():
    """Mock a single YOLO result object with one detection."""
    import torch

    result = MagicMock()
    result.names = {0: "person", 67: "cell phone"}

    boxes = MagicMock()
    boxes.xyxy = torch.tensor([[100, 100, 200, 200]])
    boxes.conf = torch.tensor([0.85])
    boxes.cls = torch.tensor([0])
    boxes.__len__ = lambda self: 1
    result.boxes = boxes

    return result


@pytest.fixture
def mock_critical_result():
    """Mock a YOLO result with a critical detection (cell phone)."""
    import torch

    result = MagicMock()
    result.names = {0: "person", 67: "cell phone"}

    boxes = MagicMock()
    boxes.xyxy = torch.tensor([[150, 150, 250, 250]])
    boxes.conf = torch.tensor([0.92])
    boxes.cls = torch.tensor([67])
    boxes.__len__ = lambda self: 1
    result.boxes = boxes

    return result


@pytest.fixture
def mock_empty_result():
    """Mock a YOLO result with no detections."""
    result = MagicMock()
    result.names = {0: "person"}
    result.boxes = None
    return result
