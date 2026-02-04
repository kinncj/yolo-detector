"""Frame annotation utilities."""

from collections import defaultdict
import logging
import cv2
import numpy as np

from yolodetector.config import AnnotationConfig

logger = logging.getLogger(__name__)


class FrameAnnotator:
    """Annotates frames with detection results."""

    def __init__(self, config: AnnotationConfig):
        self._config = config

    def draw_critical_icon(self, frame, x, y, size=24):
        half = size // 2
        pts = np.array([
            [x + half, y],
            [x, y + size],
            [x + size, y + size],
        ], dtype=np.int32)

        cv2.fillPoly(frame, [pts], self._config.critical_icon_color_bgr)
        cv2.polylines(frame, [pts], True, (0, 0, 0), 2, cv2.LINE_AA)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        text = "!"
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = x + (size - text_size[0]) // 2
        text_y = y + size - 4
        cv2.putText(frame, text, (text_x, text_y), font, font_scale,
                    (0, 0, 0), font_thickness, cv2.LINE_AA)

        return frame

    def draw_label_with_background(self, frame, text, x, y, color, thickness=2):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, font_thickness
        )

        padding = 4
        bg_color = (40, 40, 40)
        cv2.rectangle(
            frame,
            (x, y - text_height - padding),
            (x + text_width + padding * 2, y + baseline),
            bg_color,
            -1,
        )

        cv2.rectangle(
            frame,
            (x, y - text_height - padding),
            (x + text_width + padding * 2, y + baseline),
            color,
            thickness,
        )

        cv2.putText(
            frame,
            text,
            (x + padding, y - 2),
            font,
            font_scale,
            (255, 255, 255),
            font_thickness,
            cv2.LINE_AA,
        )

        return frame

    def annotate_frame(self, frame, results):
        detections_summary = defaultdict(int)
        critical_detected = []

        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].cpu().numpy().astype(int)
                conf = float(boxes.conf[i].cpu())
                cls_id = int(boxes.cls[i].cpu())
                cls_name = result.names[cls_id]

                x1, y1, x2, y2 = xyxy
                detections_summary[cls_name] += 1

                if self._config.is_critical(cls_name):
                    display_name = self._config.critical_classes[cls_name]
                    label = f"[!] CRITICAL: {display_name} {conf:.0%}"
                    color = self._config.critical_color_bgr
                    thickness = self._config.critical_thickness

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
                    self.draw_label_with_background(frame, label, x1, y1 - 5, color, thickness)

                    icon_size = 24
                    icon_x = max(0, x1 - icon_size - 4)
                    icon_y = max(0, y1 - icon_size - 4)
                    self.draw_critical_icon(frame, icon_x, icon_y, size=icon_size)

                    critical_detected.append((cls_name, conf, (x1, y1, x2, y2)))
                else:
                    color = self._config.get_color(cls_id)
                    label = f"{cls_name} {conf:.0%}"
                    thickness = self._config.normal_thickness

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
                    self.draw_label_with_background(frame, label, x1, y1 - 5, color, thickness)

        logger.debug("Frame annotated: %d detections, %d critical", sum(detections_summary.values()), len(critical_detected))
        return frame, detections_summary, critical_detected
