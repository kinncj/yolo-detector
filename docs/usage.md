# Usage Examples

Practical command-line examples for common scenarios.

---

## Basic Usage

### Single Video Detection

```bash
# Process single video with default model (yolo26x)
python main.py --input-dir videos --prefix "2026-02-04"
```

### Multiple Models

```bash
# Run detection with multiple YOLO models sequentially
python main.py --input-dir videos --prefix "2026-02-04" \
  --model "yolov8x,yolo26x,yolo12x"
```

### All Camera Angles

```bash
# Include FACE and TOP camera videos
python main.py --input-dir videos --prefix "2026-02-04" --all
```

---

## Device Selection

### Apple Silicon (MPS)

```bash
# M1/M2/M3 Mac (default)
python main.py --input-dir videos --prefix "2026-02-04" --device mps
```

### NVIDIA GPU (CUDA)

```bash
# Use CUDA for inference
python main.py --input-dir videos --prefix "2026-02-04" --device cuda
```

### Vulkan Backend

```bash
# AMD or Intel GPU
python main.py --input-dir videos --prefix "2026-02-04" --device vulkan
```

### CPU Fallback

```bash
# No GPU, slowest but always works
python main.py --input-dir videos --prefix "2026-02-04" --device cpu
```

---

## Performance Tuning

### Faster Inference (Lower Accuracy)

```bash
# Smaller image size
python main.py --input-dir videos --prefix "2026-02-04" \
  --imgsz 416 --model yolov8s

# Higher confidence (fewer detections)
python main.py --input-dir videos --prefix "2026-02-04" \
  --conf 0.5
```

### Better Accuracy (Slower)

```bash
# Larger image size
python main.py --input-dir videos --prefix "2026-02-04" \
  --imgsz 1280 --model yolo26x

# Lower confidence (more detections)
python main.py --input-dir videos --prefix "2026-02-04" \
  --conf 0.15
```

---

## Batch Processing

### Process Multiple Prefixes

```bash
#!/bin/bash
# Process all prefixes in a directory

for prefix in "2026-02-04 10-00-00" "2026-02-04 11-30-00" "2026-02-04 13-15-00"; do
    echo "Processing: $prefix"
    python main.py --input-dir videos --prefix "$prefix" --model yolo26x
done
```

### Process All Videos (No Prefix Filter)

```bash
# Use empty prefix to process all videos
python main.py --input-dir videos --prefix "" --model yolo26x
```

---

## Output Management

### Custom Output Directory

```bash
# Specify output location
python main.py --input-dir videos --prefix "2026-02-04" \
  --output-dir /tmp/detections
```

### Preserve Input Structure

```bash
# Output to input_dir/output (default)
python main.py --input-dir videos --prefix "2026-02-04"
# Results in: videos/output/2026-02-04_yolo26x_detected.mp4
```

---

## Model Comparison

### Compare Multiple Models

```bash
# Run same video through 3 models
python main.py --input-dir videos --prefix "2026-02-04 11-42-16" \
  --model "yolov8x,yolo26x,yolo12x"

# Outputs:
# - 2026-02-04 11-42-16_yolov8x_detected.mp4
# - 2026-02-04 11-42-16_yolo26x_detected.mp4
# - 2026-02-04 11-42-16_yolo12x_detected.mp4
```

### Model Family Comparison

```bash
# Test all YOLO versions
python main.py --input-dir videos --prefix "2026-02-04" \
  --model "yolo26x,yolo12x,yolo11x,yolo10x,yolo9e,yolov8x"
```

---

## Advanced Scenarios

### High-Security Monitoring

```bash
# Low confidence, catch everything
python main.py --input-dir videos --prefix "2026-02-04" \
  --conf 0.1 --model yolo26x --all
```

### Real-Time Processing (Fast)

```bash
# Smallest model, small image size
python main.py --input-dir videos --prefix "2026-02-04" \
  --model yolov8n --imgsz 320 --device cuda
```

### Maximum Accuracy (Slow)

```bash
# Largest model, large image size, low confidence
python main.py --input-dir videos --prefix "2026-02-04" \
  --model yolo26x --imgsz 1280 --conf 0.1
```

---

## Debugging

### Verify Installation

```bash
# Test imports
python -c "
import cv2
import torch
from ultralytics import YOLO
print('✓ All dependencies installed')
print('CUDA:', torch.cuda.is_available())
print('MPS:', hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
"
```

### Check Model Availability

```bash
# Download and verify model
python -c "
from ultralytics import YOLO
model = YOLO('yolo26x.pt')
print('✓ Model ready:', model.device)
"
```

### List Available Videos

```bash
# Find videos matching prefix
ls -lh videos/ | grep "2026-02-04"
```

---

## Automation

### Cron Job (Hourly Processing)

```bash
# Add to crontab: crontab -e
0 * * * * cd /path/to/yolodetector && python main.py --input-dir /data/videos --prefix "$(date +'\%Y-\%m-\%d')" --model yolo26x
```

### Watch Directory (inotify)

```bash
# Monitor directory for new videos
inotifywait -m /data/videos -e create -e moved_to |
    while read path action file; do
        python main.py --input-dir /data/videos --prefix "${file%.*}" --model yolo26x
    done
```

### Parallel Processing (GNU Parallel)

```bash
# Process multiple videos in parallel
find videos/ -name "*.mp4" | parallel -j 4 \
  python main.py --input-dir videos --prefix {/.} --model yolo26x
```

---

## Docker

### Build Image

```bash
docker build -f Dockerfile.cuda -t yolodetector:cuda .
```

### Run Container

```bash
docker run --gpus all \
  -v $(pwd)/videos:/workspace/videos \
  -v $(pwd)/output:/workspace/output \
  yolodetector:cuda \
  python main.py --input-dir /workspace/videos --prefix "2026-02-04" --device cuda
```

---

## Troubleshooting Commands

### Check GPU Utilization

```bash
# Monitor GPU while running
# Terminal 1:
python main.py --input-dir videos --prefix "2026-02-04" --device cuda

# Terminal 2:
nvidia-smi -l 1
```

### Profile Performance

```bash
# Add to main.py temporarily:
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... run pipeline ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Verify Output

```bash
# Check output video
ffprobe videos/output/2026-02-04_yolo26x_detected.mp4

# Play output
ffplay videos/output/2026-02-04_yolo26x_detected.mp4
```

---

## Environment-Specific Examples

### Apple Silicon Mac

```bash
conda activate yolodetector-apple-silicon
python main.py --input-dir videos --prefix "2026-02-04" --device mps
```

### Ubuntu with CUDA

```bash
conda activate yolodetector-ubuntu-cuda
python main.py --input-dir videos --prefix "2026-02-04" --device cuda
```

### Windows WSL2

```bash
conda activate yolodetector-wsl2-cuda
python main.py --input-dir /mnt/c/Users/kinn/Videos --prefix "2026-02-04" --device cuda
```

### NVIDIA DGX (Multi-GPU)

```bash
conda activate yolodetector-dgx-spark
python main.py --input-dir videos --prefix "2026-02-04" --device cuda
```

---

## Output Examples

### Console Output

```
Processing videos from: /Users/kinn/Movies/videos
Prefix: 2026-02-04 11-42-16
Models: yolo26x

Found 1 video(s) to process.

Processing: 2026-02-04 11-42-16_MAIN.mp4 (Model: yolo26x)
  0%|                                    | 0/12345 [00:00<?, ?it/s]
 50%|████████████                        | 6172/12345 [00:30<00:30, 205.73it/s]
100%|████████████████████████████████████| 12345/12345 [01:00<00:00, 205.75it/s]

Video Summary (yolo26x - 2026-02-04 11-42-16_MAIN.mp4):
  Total detections: 387
  Critical detections: 87 (PHONE: 87)
  Output: /Users/kinn/Movies/videos/output/2026-02-04 11-42-16_MAIN_yolo26x_detected.mp4

Final Summary:
  Total videos processed: 1
  Total detections: 387
  Critical detections: 87
```

---

## Contact

**Author**: Kinn Coelho Juliao <kinncj@gmail.com>
**License**: AGPL-3.0
