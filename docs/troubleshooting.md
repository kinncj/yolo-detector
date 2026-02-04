# Troubleshooting Guide

Common issues and solutions.

---

## Installation Issues

### `ModuleNotFoundError: No module named 'ultralytics'`

**Cause**: Environment not activated or packages not installed.

**Solution**:
```bash
# Activate correct environment
conda activate yolodetector-apple-silicon

# Verify installation
python -c "import ultralytics; print(ultralytics.__version__)"

# If still missing, reinstall
conda env remove --name yolodetector-apple-silicon --all
conda env create -f environment-apple-silicon.yml
```

---

### `CUDA out of memory` (RuntimeError: CUDA out of memory)

**Cause**: Inference image size too large for GPU memory.

**Solution**:
```bash
# Reduce image size
python main.py --input-dir videos --imgsz 416

# Use smaller model
python main.py --input-dir videos --model yolov8s

# Use CPU instead
python main.py --input-dir videos --device cpu
```

**Advanced**:
```bash
# Check GPU memory
python -c "import torch; print(torch.cuda.get_device_properties(0))"

# Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"
```

---

### `FileNotFoundError: Model 'yolo26x.pt' not found`

**Cause**: Model file missing and automatic download failed.

**Solution**:
```bash
# Check internet connection
curl -I https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26x.pt

# Manual download
wget https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26x.pt -O yolo26x.pt

# Move to Ultralytics cache
mkdir -p ~/.yolo/
mv yolo26x.pt ~/.yolo/

# Re-run (should find model now)
python main.py --input-dir videos --model yolo26x
```

---

### `OSError: [Errno 30] Read-only file system`

**Cause**: Cannot write to output directory (permissions or read-only filesystem).

**Solution**:
```bash
# Check permissions
ls -ld output/

# Fix permissions
chmod 755 output/

# Or specify writable output directory
python main.py --input-dir videos --output-dir /tmp/output
```

---

## Runtime Issues

### Video Not Detected

**Cause**: File prefix or format not matching, or directory empty.

**Solution**:
```bash
# List files in directory
ls -la /path/to/videos/

# Verify prefix matches
# Files must contain prefix in their name
# Example: "2026-02-04 11-42-16_MAIN.mp4" with --prefix "2026-02-04"

# Check supported formats
# OpenCV supports: mp4, avi, mov, mkv, flv, wmv

# Try without prefix filter
python main.py --input-dir videos --prefix ""

# Or use absolute path
python main.py --input-dir /absolute/path/to/videos
```

---

### No Detections Found

**Cause**: Confidence threshold too high, or objects not in dataset.

**Solution**:
```bash
# Lower confidence threshold
python main.py --input-dir videos --conf 0.15

# Check model accuracy on this object type
# COCO dataset includes: person, car, dog, cat, phone, etc.
# Missing: glasses, weapons (custom models needed)

# Try different model
python main.py --input-dir videos --model yolo26x

# Verify video content
ffplay videos/input.mp4  # Check if video plays and has objects
```

---

### Slow Inference (< 10 FPS)

**Cause**: CPU inference, large image size, or slow device.

**Solution**:
```bash
# Use GPU if available
python main.py --input-dir videos --device cuda

# Reduce image size
python main.py --input-dir videos --imgsz 416

# Use smaller model
python main.py --input-dir videos --model yolov8s

# Check device in use
python -c "
from ultralytics import YOLO
model = YOLO('yolo26x.pt')
print(model.device)
"
```

---

### Output File Corrupted or Cannot Play

**Cause**: Video write incomplete, codec unsupported, or frame dimensions mismatch.

**Solution**:
```bash
# Verify output file
ffprobe output/video_detected.mp4

# Try with different codec (currently mp4v)
# Edit yolodetector/video/io.py:
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Try 'mp4a' or 'avc1'

# Verify frame dimensions match original
python -c "
import cv2
cap = cv2.VideoCapture('videos/input.mp4')
print('Input:', cap.get(cv2.CAP_PROP_FRAME_WIDTH), 'x', cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
cap.release()
"
```

---

### FPS Mismatch (Video Too Fast/Slow)

**Cause**: FPS not detected correctly, or FPS fallback to 30.0 incorrect for this file.

**Solution**:
```bash
# Check actual FPS
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1:nokey=1 videos/input.mp4

# Manual FPS override (edit main.py and set in VideoConfig)
VideoConfig(
    fps=29.97,  # Set manually
    ...
)
```

---

## Device & GPU Issues

### MPS Not Available on macOS

**Cause**: Requires macOS 12.3+, Xcode Command Line Tools, PyTorch 1.12+.

**Solution**:
```bash
# Check macOS version
sw_vers -productVersion  # Should be 12.3 or later

# Install Xcode Command Line Tools
xcode-select --install

# Update PyTorch
conda activate yolodetector-apple-silicon
conda update -c pytorch pytorch

# Check again
python -c "
import torch
print('MPS available:', torch.backends.mps.is_available())
print('PyTorch version:', torch.__version__)
"
```

---

### CUDA Not Found (Windows/Linux)

**Cause**: NVIDIA driver outdated, CUDA toolkit missing, or wrong conda environment.

**Solution**:
```bash
# Check NVIDIA driver
nvidia-smi  # Should show GPU and driver version

# Check CUDA version
python -c "import torch; print(torch.version.cuda)"

# Update NVIDIA driver
# Windows: Download from nvidia.com
# Linux: sudo apt-get install nvidia-driver-XXX

# Recreate environment
conda env remove --name yolodetector-ubuntu-cuda --all
conda env create -f environment-ubuntu-cuda.yml
```

---

### Vulkan Not Working

**Cause**: Vulkan drivers not installed, or GPU doesn't support Vulkan.

**Solution**:
```bash
# Check Vulkan support
vulkaninfo 2>/dev/null | grep "GPU"

# Install Vulkan drivers
# Ubuntu: sudo apt-get install vulkan-tools libvulkan1
# Windows: Download from gpu vendor (NVIDIA, AMD, Intel)

# Fall back to CUDA or CPU
python main.py --input-dir videos --device cuda
```

---

## Multi-Model Issues

### Models Running Sequentially Too Slow

**Cause**: Processing entire video with each model.

**Solution**:
```bash
# Process subset (test with single model first)
python main.py --input-dir videos --model yolo26x

# Sample every Nth frame (edit main.py)
# Add frame counter: if frame_idx % 10 != 0: continue

# Split video into clips (4-5 min each)
ffmpeg -i input.mp4 -c copy -segment_time 300 -f segment output_%03d.mp4
```

---

### Out of Memory with Multi-Model

**Cause**: Multiple models loaded or intermediate frames buffered.

**Solution**:
```bash
# Reduce batch of models
python main.py --input-dir videos --model yolo26x

# Reduce image size
python main.py --input-dir videos --imgsz 416

# Use CPU (slower, more memory-efficient)
python main.py --input-dir videos --device cpu
```

---

## CLI & Argument Issues

### Unrecognized Arguments

**Cause**: Typo or argument format incorrect.

**Solution**:
```bash
# Check available arguments
python main.py --help

# Common mistakes:
# ✗ --input /path/to/videos          (should be --input-dir)
# ✗ --model=yolo26x                  (should be --model yolo26x)
# ✗ --conf=0.5                       (should be --conf 0.5)

# Correct:
python main.py --input-dir videos --model yolo26x --conf 0.5
```

---

### Prefix Not Matching

**Cause**: File naming doesn't include prefix.

**Solution**:
```bash
# List files
ls videos/

# If files are "video_001.mp4", use prefix accordingly
python main.py --input-dir videos --prefix "video"

# If no prefix needed
python main.py --input-dir videos --prefix ""
```

---

## WSL2 Specific Issues

### WSL2 Cannot Find Files on Windows Drive

**Cause**: Path format incorrect (Windows paths don't work directly in WSL2).

**Solution**:
```bash
# Windows path: C:\Users\kinn\Videos
# WSL2 path:    /mnt/c/Users/kinn/Videos

python main.py --input-dir /mnt/c/Users/kinn/Videos
```

---

### WSL2 CUDA Not Found

**Cause**: NVIDIA drivers not installed on Windows, or WSL2 NVIDIA integration not set up.

**Solution**:
```bash
# Install NVIDIA driver on Windows first
# https://developer.nvidia.com/cuda/wsl/download

# Inside WSL2, verify
nvidia-smi  # Should work and show GPU

# If not, update WSL2
wsl --update

# Restart WSL2
wsl --shutdown
```

---

## Performance Debugging

### Identify Bottleneck

```bash
# Check GPU utilization (while running)
# Terminal 1: Run detection
python main.py --input-dir videos --model yolo26x

# Terminal 2: Monitor GPU
nvidia-smi -l 1  # Update every 1 second

# Check CPU usage
top  # macOS
htop  # Linux
```

---

### Profile Code

```bash
import cProfile
import pstats

# Add to main.py
profiler = cProfile.Profile()
profiler.enable()

# ... run pipeline ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## Getting Help

### Collect Debug Info

```bash
# System info
python -c "
import platform
import torch
import cv2
from ultralytics import YOLO

print('OS:', platform.platform())
print('Python:', platform.python_version())
print('PyTorch:', torch.__version__)
print('CUDA:', torch.version.cuda)
print('OpenCV:', cv2.__version__)
print('Ultralytics:', YOLO('yolo26x.pt').version)
"

# GPU info (if applicable)
nvidia-smi

# Environment info
conda env export > environment_export.yml
```

### Report Issue

Email: **kinncj@gmail.com**

Include:
1. Debug info from above
2. Error message (full traceback)
3. Command you ran
4. Input file path/sample
5. Expected vs. actual result

---

## Contact

**Author**: Kinn Coelho Juliao <kinncj@gmail.com>
**License**: AGPL-3.0
