"""Tests for yolodetector.annotation.renderer."""

import numpy as np
import pytest

from yolodetector.annotation.renderer import FrameAnnotator
from yolodetector.config import AnnotationConfig


class TestFrameAnnotator:
    def test_init_stores_config(self, annotation_config):
        annotator = FrameAnnotator(annotation_config)
        assert annotator._config is annotation_config

    def test_annotate_frame_empty_results(self, sample_frame, annotation_config, mock_empty_result):
        annotator = FrameAnnotator(annotation_config)
        frame, detections, criticals = annotator.annotate_frame(sample_frame, [mock_empty_result])
        assert isinstance(frame, np.ndarray)
        assert len(detections) == 0
        assert len(criticals) == 0

    def test_annotate_frame_normal_detection(self, sample_frame, annotation_config, mock_yolo_result):
        annotator = FrameAnnotator(annotation_config)
        frame, detections, criticals = annotator.annotate_frame(sample_frame, [mock_yolo_result])
        assert "person" in detections
        assert detections["person"] == 1
        assert len(criticals) == 0

    def test_annotate_frame_critical_detection(self, sample_frame, annotation_config, mock_critical_result):
        annotator = FrameAnnotator(annotation_config)
        frame, detections, criticals = annotator.annotate_frame(sample_frame, [mock_critical_result])
        assert "cell phone" in detections
        assert len(criticals) == 1
        assert criticals[0][0] == "cell phone"

    def test_annotate_frame_returns_ndarray(self, sample_frame, annotation_config, mock_yolo_result):
        annotator = FrameAnnotator(annotation_config)
        frame, _, _ = annotator.annotate_frame(sample_frame, [mock_yolo_result])
        assert isinstance(frame, np.ndarray)
        assert frame.shape == sample_frame.shape

    def test_annotate_frame_no_results(self, sample_frame, annotation_config):
        annotator = FrameAnnotator(annotation_config)
        frame, detections, criticals = annotator.annotate_frame(sample_frame, [])
        assert len(detections) == 0
        assert len(criticals) == 0
