"""Model loading and inference utilities."""

import logging
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

from ultralytics import YOLO

logger = logging.getLogger(__name__)

try:
    from ultralytics.utils.downloads import attempt_download
except Exception:  # pragma: no cover - optional dependency path
    attempt_download = None


class YoloDetector:
    """Encapsulates YOLO model loading and inference."""

    def __init__(self, model_name: str):
        model_path = self._resolve_model_path(model_name)
        self._model = YOLO(model_path)
        self.names = self._model.names
        logger.info("Model loaded: %s (%d classes)", model_name, len(self.names))

    @staticmethod
    def _resolve_model_path(model_name: str) -> str:
        normalized_name = model_name if model_name.endswith(".pt") else f"{model_name}.pt"
        logger.debug("Resolving model path for: %s (normalized: %s)", model_name, normalized_name)

        path = Path(model_name)
        if path.exists():
            logger.info("Using local model file: %s", path)
            return str(path)

        path_normalized = Path(normalized_name)
        if path_normalized.exists():
            logger.info("Using local model file (normalized): %s", path_normalized)
            return str(path_normalized)

        if attempt_download is not None:
            try:
                result = str(attempt_download(normalized_name))
                logger.info("Downloaded model via attempt_download: %s", result)
                return result
            except Exception:
                logger.debug("attempt_download failed for %s, trying original name", normalized_name)
                try:
                    result = str(attempt_download(model_name))
                    logger.info("Downloaded model via attempt_download (original name): %s", result)
                    return result
                except Exception:
                    logger.warning("attempt_download failed for both %s and %s", normalized_name, model_name)

        downloaded = YoloDetector._download_from_ultralytics_assets(normalized_name)
        if downloaded is not None:
            logger.info("Downloaded from ultralytics assets: %s", downloaded)
            return downloaded

        logger.warning("Could not resolve model, falling back to: %s", normalized_name)
        return normalized_name

    @staticmethod
    def _download_from_ultralytics_assets(model_name: str) -> Optional[str]:
        filename = Path(model_name).name
        target = Path(model_name)
        if target.parent == Path("."):
            target = Path.cwd() / filename
        target.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://github.com/ultralytics/assets/releases/download/v8.4.0/{filename}"
        logger.debug("Attempting download from ultralytics assets: %s", url)
        try:
            urlretrieve(url, target)
            if target.exists():
                return str(target)
        except Exception:
            logger.warning("Download from ultralytics assets failed: %s", url)
            return None

        return None

    def predict(self, frame, *, device: str, conf: float, iou: float, imgsz: Optional[int]):
        kwargs = {
            "device": device,
            "conf": conf,
            "iou": iou,
            "verbose": False,
        }
        if imgsz is not None:
            kwargs["imgsz"] = imgsz
        return self._model(frame, **kwargs)
