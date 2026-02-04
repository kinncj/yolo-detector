"""Tests for yolodetector.reporting.summary."""

import pytest
from yolodetector.reporting.summary import ReportAggregator, VideoReport


class TestVideoReport:
    def test_default_factory(self):
        report = VideoReport()
        assert len(report.detections) == 0
        assert len(report.criticals) == 0
        assert report.output_path == ""


class TestReportAggregator:
    @pytest.fixture
    def aggregator(self):
        return ReportAggregator(critical_classes={"cell phone": "PHONE"})

    @pytest.fixture
    def sample_report(self):
        return VideoReport(
            detections={"person": 100, "cell phone": 5},
            criticals=[(10, "cell phone", 0.92, (150, 150, 250, 250))],
            output_path="output/test_detected.mp4"
        )

    def test_record_video(self, aggregator, sample_report):
        aggregator.record_video("test.mp4", sample_report)
        assert "test.mp4" in aggregator._videos

    def test_print_video_summary_with_detections(self, aggregator, sample_report, capsys):
        aggregator.print_video_summary(sample_report)
        captured = capsys.readouterr()
        assert "Total detections: 105" in captured.out
        assert "person" in captured.out
        assert "[CRITICAL]" in captured.out
        assert "CRITICAL OBJECTS DETECTED" in captured.out

    def test_print_video_summary_no_detections(self, aggregator, capsys):
        report = VideoReport()
        aggregator.print_video_summary(report)
        captured = capsys.readouterr()
        assert "Total detections: 0" in captured.out
        assert "CRITICAL OBJECTS DETECTED" not in captured.out

    def test_print_final_summary(self, aggregator, sample_report, capsys):
        aggregator.record_video("test.mp4", sample_report)
        aggregator.print_final_summary(10.5)
        captured = capsys.readouterr()
        assert "PROCESSING COMPLETE" in captured.out
        assert "10.5s" in captured.out
        assert "Videos processed: 1" in captured.out
        assert "TOTAL CRITICAL OBJECTS ACROSS ALL VIDEOS: 1" in captured.out

    def test_print_final_summary_no_criticals(self, aggregator, capsys):
        report = VideoReport(detections={"person": 50}, criticals=[], output_path="out.mp4")
        aggregator.record_video("clean.mp4", report)
        aggregator.print_final_summary(5.0)
        captured = capsys.readouterr()
        assert "TOTAL CRITICAL OBJECTS" not in captured.out


class TestExportJson:
    @pytest.fixture
    def aggregator(self):
        return ReportAggregator(critical_classes={"cell phone": "PHONE"})

    @pytest.fixture
    def sample_report(self):
        return VideoReport(
            detections={"person": 100, "cell phone": 5},
            criticals=[(10, "cell phone", 0.92, (150, 150, 250, 250))],
            output_path="output/test_detected.mp4"
        )

    def test_export_creates_file(self, aggregator, sample_report, tmp_path):
        aggregator.record_video("test.mp4", sample_report)
        output = tmp_path / "report.json"
        aggregator.export_json(str(output), 10.5)
        assert output.exists()

    def test_export_json_content(self, aggregator, sample_report, tmp_path):
        import json
        aggregator.record_video("test.mp4", sample_report)
        output = tmp_path / "report.json"
        aggregator.export_json(str(output), 10.5)
        data = json.loads(output.read_text())
        assert data["total_time_seconds"] == 10.5
        assert data["videos_processed"] == 1
        assert "test.mp4" in data["videos"]
        assert data["videos"]["test.mp4"]["total_detections"] == 105
