# CLI Reference

## Synopsis

```bash
python main.py [OPTIONS]
```

Processes video files using YOLO object detection, annotates frames with bounding boxes and labels, and marks critical objects (e.g., cell phones) with distinctive visual indicators.

---

## Command-Line Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--all` | bool | `False` | Process all camera angles (main, FACE, TOP) instead of main video only |
| `--include-cameras` | bool | `False` | Alias for `--all` |
| `--input-dir` | Path | `"."` | Directory containing input video files |
| `--output-dir` | Path | `<input-dir>/output` | Directory for output annotated videos |
| `--prefix` | str | `"dummy"` | File prefix to search for (e.g., `"2026-02-04 10-17-17"`) |
| `--conf` | float | `0.25` | Confidence threshold (0.0-1.0). Lower = more detections, more false positives |
| `--iou` | float | `0.45` | IoU threshold for Non-Maximum Suppression (0.0-1.0) |
| `--imgsz` | int | `None` | Inference image size (e.g., 640, 1280). If not set, uses model default |
| `--model` | str | `"yolo26x.pt"` | YOLO model(s) to use (comma-separated for multi-model comparison) |
| `--device` | str | `"mps"` | Device for inference: `cpu`, `cuda`, `mps` (Apple Silicon), `vulkan` |
| `--log-level` | str | `"WARNING"` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `--report-json` | Path | `None` | Path to write structured JSON report file |

---

## Usage Examples

### Basic: Process Main Video Only

```bash
python main.py
```

Processes the main video file matching the default prefix in the current directory.

**Output:**
- `./output/<prefix>_detected.mp4`

---

### Process All Camera Angles

```bash
python main.py --all
```

or

```bash
python main.py --include-cameras
```

Processes main video plus FACE and TOP camera angles.

**Output:**
- `./output/<prefix>_detected.mp4`
- `./output/<prefix>_FACE_detected.mp4`
- `./output/<prefix>_TOP_detected.mp4`

---

### Custom Input/Output Directories

```bash
python main.py --input-dir /path/to/videos --output-dir /path/to/results
```

Reads videos from `/path/to/videos` and writes annotated videos to `/path/to/results`.

---

### Custom File Prefix

```bash
python main.py --prefix "2026-02-04 10-17-17"
```

Searches for files starting with `2026-02-04 10-17-17.mp4`, `2026-02-04 10-17-17_FACE.mp4`, etc.

---

### Lower Confidence Threshold (More Detections)

```bash
python main.py --conf 0.15
```

Detects more objects but may increase false positives. Useful for ensuring critical objects are not missed.

---

### Use Different YOLO Model

```bash
python main.py --model yolov8n.pt
```

Uses a smaller, faster model (`yolov8n.pt`) instead of the default `yolo26x.pt`. Trade-off: faster inference, lower accuracy.

**Available models:**
- `yolov8n.pt` — Nano (fastest, lowest accuracy)
- `yolov8s.pt` — Small
- `yolov8m.pt` — Medium
- `yolov8x.pt` — Extra large (slower, higher accuracy)
- `yolo26x.pt` — Default (best accuracy for critical object detection)

---

### Explicit Inference Size

```bash
python main.py --imgsz 640
```

Scales frames to 640px for inference. Smaller values = faster inference, may reduce accuracy on small objects.

---

### CPU Inference (No GPU/MPS)

```bash
python main.py --device cpu
```

Forces CPU inference. Slower than GPU/MPS but works on any machine.

---

### CUDA (NVIDIA GPU)

```bash
python main.py --device cuda
```

Uses NVIDIA GPU via CUDA. Requires CUDA-enabled PyTorch installation.

---

### MPS (Apple Silicon)

```bash
python main.py --device mps
```

Default on macOS with Apple Silicon (M1/M2/M3). Uses Metal Performance Shaders for acceleration.

---

### Enable Debug Logging

```bash
python main.py --log-level DEBUG
```

Shows detailed operational logs including model resolution steps, file operations, and frame processing statistics.

**Log levels:**
- `DEBUG` — Verbose operational details (model path resolution, frame counts)
- `INFO` — Key operations (model loaded, video opened, writer created)
- `WARNING` — Fallback decisions and potential issues (default)
- `ERROR` — Only show errors

---

### Export JSON Report

```bash
python main.py --report-json report.json
```

Exports structured detection results to a JSON file for programmatic consumption.

**JSON format:**
```json
{
  "total_time_seconds": 45.3,
  "videos_processed": 1,
  "total_criticals": 3,
  "videos": {
    "clip.mp4": {
      "detections": {"person": 100, "cell phone": 5},
      "total_detections": 105,
      "criticals": [
        {
          "frame": 245,
          "class": "cell phone",
          "confidence": 0.92,
          "bbox": [150, 150, 250, 250]
        }
      ],
      "output_path": "output/clip_yolo26x_detected.mp4"
    }
  }
}
```

---

### Multi-Model Comparison

```bash
python main.py --model "yolov8x,yolo26x,yolo12x"
```

Runs multiple YOLO models sequentially and generates separate outputs for each:
- `<prefix>_yolov8x_detected.mp4`
- `<prefix>_yolo26x_detected.mp4`
- `<prefix>_yolo12x_detected.mp4`

Useful for comparing model performance and accuracy.

---

## Combined Example

```bash
python main.py \
  --all \
  --input-dir /Volumes/Video/2026-02-04 \
  --output-dir /Users/analyst/results \
  --prefix "2026-02-04 10-17-17" \
  --conf 0.20 \
  --model yolo26x \
  --device mps \
  --log-level INFO \
  --report-json /Users/analyst/results/detection_report.json
```

Processes all camera angles from a custom directory, uses a lower confidence threshold, enables INFO logging for operational visibility, and exports a structured JSON report.

---

## Exit Codes

- `0` — Success
- `1` — Error (model load failure, missing input files, etc.)

---

## Output Format

### Annotated Video Files

- Codec: `mp4v`
- FPS: Same as input video
- Resolution: Same as input video
- Annotations:
  - Bounding boxes (colored by class)
  - Labels with confidence percentage
  - Critical objects: red boxes, yellow warning triangle icon, `[!] CRITICAL` label

### Console Output

```
======================================================================
YOLO Object Detection with Critical Object Marking
======================================================================
Model: yolo26x.pt
Device: mps
Confidence threshold: 0.25
IoU threshold: 0.45
Image size: None
Critical classes: ['cell phone']

...

======================================================================
Processing: 2026-02-04 10-17-17.mp4
======================================================================
Resolution: 1280x720
FPS: 30.00
Total frames: 18000

Processing: 100%|████████████████████| 18000/18000 [12:30<00:00, 24.00 frame/s]

Completed in 750.2s (24.00 FPS)
Output saved to: ./output/2026-02-04 10-17-17_detected.mp4

Total detections: 4523

Detection breakdown:
  person              :   1234
  chair               :    456
  laptop              :    123
  cell phone          :     67 [CRITICAL]

**********************************************************************
*** CRITICAL OBJECTS DETECTED: 67 instances ***
**********************************************************************
  Frame      0: cell phone       (87%) at (123, 456, 234, 567)
  Frame    234: cell phone       (92%) at (345, 678, 456, 789)
  ...

======================================================================
PROCESSING COMPLETE
======================================================================
Total time: 750.2s
Videos processed: 1

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
TOTAL CRITICAL OBJECTS ACROSS ALL VIDEOS: 67
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Output files:
  2026-02-04 10-17-17_detected.mp4
```

---

## Help

```bash
python main.py --help
```

Displays full CLI documentation.

---

## Related Documentation

- [Architecture](architecture.md) — System design and data flow
- [Configuration Guide](configuration.md) — Config dataclass reference
- [Development Guide](development.md) — Setup and contribution workflow
