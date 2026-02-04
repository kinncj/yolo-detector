# Setup Guide

Step-by-step instructions for all platforms.

---

## Prerequisites

- **Python**: 3.10 or 3.11 (3.12 not yet supported by Ultralytics)
- **Conda**: Installed and in PATH
- **Storage**: ~5 GB for models and outputs
- **Internet**: For model downloads (one-time)

---

## macOS Setup

### Apple Silicon (M1/M2/M3)

```bash
# Clone or download repo
cd /path/to/yolodetector

# Create environment
conda env create -f environment-apple-silicon.yml

# Activate
conda activate yolodetector-apple-silicon

# Verify
python -c "import torch; print(torch.backends.mps.is_available())"  # Should print True
```

### Intel Mac

```bash
# Create environment
conda env create -f environment-intel-mac.yml

# Activate
conda activate yolodetector-intel-mac

# Verify (CPU-only, torch should load without GPU)
python -c "import torch; print(torch.cuda.is_available())"  # Should print False
```

---

## Linux Setup

### Ubuntu with CUDA (12.1)

**Prerequisites**:
- NVIDIA GPU (RTX 3050 or better recommended)
- NVIDIA Driver installed: `nvidia-smi` should work
- CUDA 12.1 Toolkit

```bash
# Create environment
conda env create -f environment-ubuntu-cuda.yml

# Activate
conda activate yolodetector-ubuntu-cuda

# Verify
python -c "import torch; print(torch.cuda.is_available())"  # Should print True
python -c "import torch; print(torch.cuda.get_device_name(0))"  # Should print GPU name
```

### Ubuntu with Vulkan

For AMD or Intel integrated GPUs:

```bash
conda env create -f environment-ubuntu-vulkan.yml
conda activate yolodetector-ubuntu-vulkan

# Verify Vulkan is available
python -c "import torch; print('vulkan' in dir(torch.backends))"
```

### Ubuntu ARM (Raspberry Pi, etc.)

```bash
conda env create -f environment-ubuntu-arm.yml
conda activate yolodetector-ubuntu-arm

# Note: CPU-only, slower inference
```

---

## Windows Setup

### Windows with CUDA

**Prerequisites**:
- NVIDIA GPU and drivers (`nvidia-smi` works)
- Visual Studio Build Tools or MinGW

```powershell
# PowerShell (administrator recommended)
conda env create -f environment-windows-cuda.yml
conda activate yolodetector-windows-cuda

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### Windows with Vulkan

```powershell
conda env create -f environment-windows-vulkan.yml
conda activate yolodetector-windows-vulkan
```

### Windows ARM

```powershell
# ARM64 system only
conda env create -f environment-windows-arm.yml
conda activate yolodetector-windows-arm
```

### Windows CPU

```powershell
# No GPU, CPU inference only
conda env create -f environment-windows-cpu.yml
conda activate yolodetector-windows-cpu
```

---

## WSL2 Setup (Windows Subsystem for Linux 2)

### Prerequisites

1. **Install WSL2**:
   ```powershell
   wsl --install Ubuntu-22.04
   ```

2. **Inside WSL2 terminal**:
   ```bash
   sudo apt-get update && sudo apt-get install -y build-essential libssl-dev
   ```

3. **Install Conda**:
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

### WSL2 with CUDA

**Prerequisites**: NVIDIA drivers installed on Windows (not WSL2). WSL2 will auto-detect.

```bash
conda env create -f environment-wsl2-cuda.yml
conda activate yolodetector-wsl2-cuda

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### WSL2 with Vulkan

```bash
conda env create -f environment-wsl2-vulkan.yml
conda activate yolodetector-wsl2-vulkan
```

### WSL2 CPU

```bash
conda env create -f environment-wsl2-cpu.yml
conda activate yolodetector-wsl2-cpu
```

---

## NVIDIA DGX Setup

For multi-GPU clusters with Spark:

```bash
conda env create -f environment-dgx-spark.yml
conda activate yolodetector-dgx-spark

# Verify multi-GPU
python -c "import torch; print(torch.cuda.device_count())"
```

---

## First Run

### 1. Test Installation

```bash
# Activate environment
conda activate yolodetector-apple-silicon  # or your environment

# Test imports
python -c "
import cv2
import torch
import ultralytics
print('✓ All dependencies installed')
"
```

### 2. Download Models

Models auto-download on first use, but you can pre-download:

```bash
python -c "
from ultralytics import YOLO
YOLO('yolo26x.pt')  # Downloads yolo26x
YOLO('yolov8x.pt')  # Downloads yolov8x
print('✓ Models ready')
"
```

### 3. Run Detection

```bash
# Place test video in a folder
mkdir -p test_videos
cp /path/to/your/video.mp4 test_videos/

# Run detection
python main.py --input-dir test_videos --prefix "test" --model yolo26x

# Check output
ls test_videos/output/
# Should see: test_yolo26x_detected.mp4
```

---

## Device Selection

### Automatic Detection

```bash
python main.py --input-dir videos --device auto  # Picks best available
```

### Manual Selection

```bash
# Apple Silicon
python main.py --input-dir videos --device mps

# NVIDIA CUDA
python main.py --input-dir videos --device cuda

# Vulkan
python main.py --input-dir videos --device vulkan

# CPU (fallback)
python main.py --input-dir videos --device cpu
```

### Check Available Devices

```bash
python -c "
import torch
print('CUDA:', torch.cuda.is_available())
print('MPS:', hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
print('CPU:', torch.backends.cpu.is_available())
"
```

---

## Troubleshooting Setup

### Model Download Fails

```bash
# Check internet connection
curl -I https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26x.pt

# Manual download
wget https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26x.pt

# Move to Ultralytics cache
mkdir -p ~/.yolo
mv yolo26x.pt ~/.yolo/
```

### CUDA Not Found

```bash
# Verify NVIDIA drivers
nvidia-smi

# Check CUDA in environment
python -c "import torch; print(torch.version.cuda)"

# Re-create environment with correct CUDA version
conda remove --name yolodetector-ubuntu-cuda --all
conda env create -f environment-ubuntu-cuda.yml
```

### MPS Not Available (macOS)

```bash
# Requires macOS 12.3+, Xcode Command Line Tools, PyTorch 1.12+
xcode-select --install

# Update PyTorch
conda update -c pytorch pytorch
```

### Import Errors

```bash
# Reinstall from scratch
conda env remove --name yolodetector-apple-silicon
conda env create -f environment-apple-silicon.yml
conda activate yolodetector-apple-silicon
```

---

## Environment Management

### List Environments

```bash
conda env list
```

### Activate/Deactivate

```bash
conda activate yolodetector-apple-silicon
conda deactivate
```

### Update Environment

```bash
conda env update -f environment-apple-silicon.yml --prune
```

### Remove Environment

```bash
conda env remove --name yolodetector-apple-silicon
```

---

## Performance Tuning

### For Faster Inference
```bash
# Smaller image size
python main.py --input-dir videos --imgsz 416

# Lower confidence threshold
python main.py --input-dir videos --conf 0.5

# Use smaller model
python main.py --input-dir videos --model yolov8s
```

### For Better Accuracy
```bash
# Larger image size
python main.py --input-dir videos --imgsz 1280

# Higher confidence threshold
python main.py --input-dir videos --conf 0.15

# Use larger model
python main.py --input-dir videos --model yolo26x
```

---

## Docker (Optional)

For reproducible, containerized setup:

```bash
# Build image
docker build -f Dockerfile.cuda -t yolodetector:cuda .

# Run container
docker run --gpus all -v $(pwd):/workspace yolodetector:cuda \
  python main.py --input-dir /workspace/videos
```

---

## Contact

Issues? Email: <kinncj@gmail.com>
