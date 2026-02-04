# Architecture Overview

YOLO DETECTOR is built on Clean Architecture principles with SOLID design and agent-based responsibilities.

---

## System Design

### Core Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│                  (CLI Orchestration)                    │
└──┬────────────────────────────────────────────────────┬──┘
   │                                                      │
   ├─→ DetectionAgent         ├─→ AnnotationAgent        │
   │   (YOLO Inference)        │   (Frame Rendering)      │
   │                           │                          │
   └─→ VideoIOAgent           ├─→ ReportingAgent         │
       (Video I/O)             │   (Statistics & Logs)    │
       │                       │                          │
       └──────────────→ ConfigAgent ←────────────────────┘
                    (Configuration)
```

### Agent Definitions

#### 1. **DetectionAgent** (`yolodetector/models/detector.py`)

**Responsibility**: Load YOLO models and execute inference.

**Key Methods**:
- `__init__(config)`: Initialize with DetectionConfig
- `detect(frame)`: Run inference on a single frame, return YOLOv8 Results
- `_resolve_model_path(model_name)`: Locate or download model weights
- `_download_from_ultralytics_assets(model_name)`: Fallback download from GitHub

**Owned Decisions**:
- Device selection (cuda, mps, cpu, vulkan)
- Inference parameters (confidence, IoU, image size)
- Model resolution and auto-download strategy

**Design Notes**:
- No logging side effects; errors bubble up to caller
- Model loaded once at initialization
- Results returned as ultralytics.results.Results objects
- Confidence/IoU thresholds applied by YOLO during inference

#### 2. **AnnotationAgent** (`yolodetector/annotation/renderer.py`)

**Responsibility**: Render bounding boxes, labels, and critical object indicators.

**Key Methods**:
- `annotate_frame(frame, results)`: Draw boxes, labels, and icons
- `draw_critical_icon(frame, x, y)`: Draw warning triangle for critical objects
- `draw_label_with_background(frame, text, x, y)`: Render label with colored box

**Owned Decisions**:
- Palette/color selection for each class
- Box thickness and label font sizing
- Critical object visual styling (red, warning triangle, [!] label)

**Design Notes**:
- Pure function; modifies frame in-place but returns it for chaining
- Color palette (BGR format) defined in config
- Critical classes hardcoded to `["cell phone"]` (COCO limitation)

#### 3. **VideoIOAgent** (`yolodetector/video/io.py`)

**Responsibility**: Video capture and writer initialization with robust error handling.

**Key Methods**:
- `open_capture(path: Path)`: Open video file, return (VideoCapture, VideoProperties)
- `create_writer(output_path, fps, width, height)`: Initialize mp4v writer
- `VideoProperties`: Dataclass with fps, width, height, frame_count

**Owned Decisions**:
- FPS fallback logic (default 30.0 if detected FPS ≤ 0)
- Codec selection (mp4v for cross-platform compatibility)
- File validation and existence checks

**Design Notes**:
- Returns tuples for frame iteration: `while ret, frame in cap`
- FPS fallback prevents 0-FPS divide-by-zero errors
- Writer created per model to support multi-model output

#### 4. **ReportingAgent** (`yolodetector/reporting/summary.py`)

**Responsibility**: Aggregate detection statistics and critical findings.

**Key Methods**:
- `add_result(class_name, confidence, is_critical)`: Record a detection
- `print_video_summary(model_name, video_name)`: Per-video report
- `print_final_summary()`: Global statistics across all videos/models

**Owned Decisions**:
- Statistics format and grouping
- Summary output layout and verbosity
- Critical vs. normal detection classification

**Design Notes**:
- Aggregates frame-by-frame results into per-video and global buckets
- Critical detections counted separately for easy identification
- Summary printed to stdout (no logging framework dependency)

#### 5. **ConfigAgent** (`yolodetector/config.py`)

**Responsibility**: Centralized configuration and defaults.

**Key Classes**:
- `DetectionConfig`: Model, device, inference parameters
- `VideoConfig`: Input/output paths, file discovery
- `AnnotationConfig`: Colors, classes, rendering styles
- `ApplicationConfig`: Composite config with factory method

**Factory Methods**:
- `ApplicationConfig.create_default()`: Sensible defaults

**Design Notes**:
- All classes are dataclasses for immutability
- CLI arguments mapped directly to config fields
- No side effects; pure data structures

---

## Data Flow

### Multi-Model Pipeline

```
Input Video (e.g., "2026-02-04 11-42-16.mp4")
       │
       ├─→ [Model 1: yolov8x]
       │        │
       │        ├─→ DetectionAgent (inference)
       │        ├─→ AnnotationAgent (rendering)
       │        ├─→ VideoIOAgent (write)
       │        └─→ ReportingAgent (stats)
       │
       ├─→ [Model 2: yolo26x]
       │        │
       │        ├─→ DetectionAgent (inference)
       │        ├─→ AnnotationAgent (rendering)
       │        ├─→ VideoIOAgent (write)
       │        └─→ ReportingAgent (stats)
       │
       └─→ [Model N: ...]
               │
               └─→ Output files:
                   - "2026-02-04 11-42-16_yolov8x_detected.mp4"
                   - "2026-02-04 11-42-16_yolo26x_detected.mp4"
```

### Frame Processing Loop

```
for frame_idx, (ret, frame) in enumerate(video_frames):
    ├─→ DetectionAgent.detect(frame)  → Results
    │                                    (detections + metadata)
    │
    ├─→ ReportingAgent.add_result()   → Count stats
    │
    ├─→ AnnotationAgent.annotate_frame() → Annotated frame
    │
    └─→ VideoIOAgent.write(frame)     → Output file
```

---

## SOLID Principles

### Single Responsibility
- Each agent owns one aspect (detection, annotation, I/O, reporting)
- Config holds configuration; agents don't manage it

### Open/Closed
- New models added via CLI (comma-separated); no code changes
- New annotation styles added by extending AnnotationConfig
- New reports added by extending ReportingAgent

### Liskov Substitution
- All agents follow consistent interface (receive config, return data)
- VideoCapture/VideoWriter used via OpenCV API (interchangeable)

### Interface Segregation
- Agents don't expose internal methods; only public APIs
- Config classes expose only needed fields (no god objects)

### Dependency Inversion
- Agents depend on config abstractions, not concrete implementations
- main.py injects dependencies (CLI → config → agents)

---

## Error Handling

### Model Resolution
1. Check local path (e.g., `yolo26x.pt`)
2. Normalize name (add `.pt` if missing)
3. Attempt ultralytics download via `attempt_download()`
4. Fallback to GitHub assets: `https://github.com/ultralytics/assets/releases/download/v8.4.0/{model}.pt`
5. Raise `FileNotFoundError` if all strategies fail

### Video I/O
- File existence checked before opening
- FPS fallback to 30.0 if invalid
- VideoCapture property extraction wrapped in try-except
- Missing output directories created automatically

### Inference
- Confidence/IoU thresholds applied by YOLO
- Empty results (no detections) handled gracefully
- Frame dimensions preserved (no resizing)

---

## Performance Considerations

### Model Selection
| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| yolov8n | 60 FPS | 37% mAP | Real-time, CPU |
| yolov8s | 45 FPS | 44% mAP | Balanced |
| yolov8x | 25 FPS | 53% mAP | High accuracy |
| yolo26x | 30 FPS | 57% mAP | Latest, best accuracy |

### Optimization Tips
- **Reduce imgsz**: `--imgsz 416` (default 640, faster but less accurate)
- **Increase confidence**: `--conf 0.5` (fewer false positives, faster filtering)
- **Use CPU for debugging**: `--device cpu` (slower but deterministic)
- **Batch processing**: Process multiple videos in sequence with a shell loop

### Hardware Acceleration
- **MPS** (Apple Silicon): Native, fastest on M1/M2/M3
- **CUDA** (NVIDIA): Fastest on high-end GPUs (RTX 4090, etc.)
- **Vulkan**: Portable, works on AMD/Intel GPUs
- **CPU**: No GPU, slowest but always available

---

## Testing Strategy

### Unit Tests
- `test_detector.py`: Model resolution, download fallback, inference
- `test_renderer.py`: Frame annotation, color application
- `test_video_io.py`: Capture/writer creation, FPS fallback
- `test_reporter.py`: Statistics aggregation
- `test_config.py`: Config validation and factory

### Integration Tests
- Multi-model sequential processing
- End-to-end video transformation
- Critical object detection accuracy

### Mocking Strategy
- Mock YOLO model (return fixed Results objects)
- Mock VideoCapture (return synthetic frames)
- Mock file I/O (use tempfile for output)

---

## Maintenance Guidelines

### Adding New Features
1. Define agent responsibility (detection, annotation, I/O, reporting, or config)
2. Extend relevant agent class
3. Update ConfigAgent if new CLI flags needed
4. Update AGENTS.md with new skills
5. Add unit tests before deployment

### Backward Compatibility
- Preserve CLI argument names (add `--deprecated-flag` if renamed)
- Maintain default model behavior (yolo26x.pt)
- Keep output directory structure (input_dir/output)

### Common Modifications

**Add new detection class**:
```python
# Update critical_classes in AnnotationConfig
AnnotationConfig(
    critical_classes=["cell phone", "weapon"],
    ...
)
```

**Change output format**:
```python
# Extend ReportingAgent.print_video_summary()
# Update filename template in main.py
```

**Add GPU support**:
```python
# Test in environment-*.yml
# Run: python main.py --device vulkan
```

---

## Dependencies

### Core
- **ultralytics**: YOLO model management
- **opencv-python**: Video I/O, frame manipulation
- **torch**: Deep learning backend
- **numpy**: Array operations
- **tqdm**: Progress bars

### Platform-Specific
- **pytorch::pytorch-cuda**: CUDA support (optional)
- **pytorch::pytorch-vulkan**: Vulkan support (optional)
- **pytorch::pytorch-metal**: MPS support (macOS)

### Development (Optional)
- **pytest**: Unit testing
- **black**: Code formatting
- **pylint**: Linting

---

## Contact & License

**Author**: Kinn Coelho Juliao <kinncj@gmail.com>
**License**: AGPL-3.0
