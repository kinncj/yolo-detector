"""Integration tests across modules."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from yolodetector.annotation.renderer import FrameAnnotator
from yolodetector.config import AnnotationConfig, ApplicationConfig
from yolodetector.reporting.summary import ReportAggregator, VideoReport


class TestAnnotationToReportingPipeline:
    """Test that FrameAnnotator output feeds correctly into ReportAggregator."""

    def test_detection_flow(self, sample_frame, mock_yolo_result, mock_critical_result):
        config = AnnotationConfig()
        annotator = FrameAnnotator(config)
        reporter = ReportAggregator(config.critical_classes)

        # Simulate processing two frames
        _, det1, crit1 = annotator.annotate_frame(sample_frame.copy(), [mock_yolo_result])
        _, det2, crit2 = annotator.annotate_frame(sample_frame.copy(), [mock_critical_result])

        # Aggregate as main.py does
        detections = {}
        criticals = []
        for det in [det1, det2]:
            for cls_name, count in det.items():
                detections[cls_name] = detections.get(cls_name, 0) + count
        for idx, crit in enumerate([crit1, crit2]):
            for c in crit:
                criticals.append((idx, *c))

        report = VideoReport(detections=detections, criticals=criticals, output_path="test_out.mp4")
        reporter.record_video("test.mp4", report)

        assert report.detections["person"] == 1
        assert report.detections["cell phone"] == 1
        assert len(report.criticals) == 1


class TestApplicationConfigFactory:
    def test_create_default_produces_valid_config(self):
        cfg = ApplicationConfig.create_default()
        assert cfg.detection.model_name == "yolo26x.pt"
        assert cfg.annotation.is_critical("cell phone")
        assert not cfg.annotation.is_critical("person")
