# YOLO DETECTOR

[![Tests](https://github.com/kinncj/yolo-detector/actions/workflows/test.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/test.yml)
[![Lint](https://github.com/kinncj/yolo-detector/actions/workflows/lint.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/lint.yml)
[![CI](https://github.com/kinncj/yolo-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kinncj/yolo-detector/branch/main/graph/badge.svg)](https://codecov.io/gh/kinncj/yolo-detector)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Multi-model YOLO testing and comparison framework for object detection.**

Test and compare multiple YOLO versions (YOLO8, YOLO9, YOLO10, YOLO11, YOLO12, YOLO26) with support for critical object marking, multi-GPU acceleration, and batch processing across diverse hardware platforms.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Critical Classes](#critical-classes)
- [Supported Platforms](#supported-platforms)
- [Performance](#performance)
- [Documentation](#documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Multi-model inference**: Run multiple YOLO versions in sequence (YOLO8, YOLO9, YOLO10, YOLO11, YOLO12, YOLO26)
- **Critical object marking**: Automatic detection and visual flagging of sensitive objects
- **Hardware acceleration**: Native support for MPS (Apple Silicon), CUDA, Vulkan, and CPU inference
- **Cross-platform**: macOS (Intel/Apple Silicon), Windows (native/WSL2), Ubuntu, NVIDIA DGX
- **Batch processing**: Handle multiple video files and camera angles simultaneously
- **Model auto-download**: Automatic retrieval of missing YOLO weights
- **Structured logging**: Configurable log levels with operational visibility
- **JSON reporting**: Structured detection reports for programmatic consumption
- **Clean architecture**: SOLID principles, dependency injection, comprehensive test suite

---

## Quick Start

### 1. Setup Environment

```bash
# Apple Silicon Mac
conda env create -f environment-apple-silicon.yml
conda activate yolodetector-apple-silicon

# Intel Mac
conda env create -f environment-intel-mac.yml
conda activate yolodetector-intel-mac

# Ubuntu with CUDA
conda env create -f environment-ubuntu-cuda.yml
conda activate yolodetector-ubuntu-cuda

# Windows with CUDA
conda env create -f environment-windows-cuda.yml
conda activate yolodetector-windows-cuda

# WSL2 with CUDA
conda env create -f environment-wsl2-cuda.yml
conda activate yolodetector-wsl2-cuda
```

### 2. Run Detection

```bash
# Single model
python main.py --input-dir /path/to/videos --prefix "2026-02-04" --model yolo26x

# Multiple models
python main.py --input-dir /path/to/videos --prefix "2026-02-04" --model "yolov8x,yolo26x"

# All camera angles
python main.py --input-dir /path/to/videos --prefix "2026-02-04" --all
```

### 3. Output

Annotated videos saved as:
- `<prefix>_<model>_detected.mp4`

Critical detections logged with timestamps and confidence scores.

---

## Installation

### Prerequisites

- Python 3.10 or 3.11
- Conda or Miniconda (recommended for environment management)
- FFmpeg (for video processing)

### Step 1: Create Environment

Choose the environment file matching your platform from the [Supported Platforms](#supported-platforms) table.

```bash
# Example: Apple Silicon Mac
conda env create -f environment-apple-silicon.yml
conda activate yolodetector-apple-silicon
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python main.py --help
```

For detailed platform-specific setup instructions, see [docs/setup.md](docs/setup.md).

---

## Configuration

### CLI Arguments

```
--input-dir DIR              Input video directory
--output-dir DIR             Output directory (default: input_dir/output)
--prefix STR                 File prefix to search for
--model STR                  Model(s) to use (comma-separated)
--all, --include-cameras     Include FACE and TOP camera videos
--conf FLOAT                 Confidence threshold (0-1)
--iou FLOAT                  IoU threshold for NMS
--imgsz INT                  Inference image size
--device STR                 Device: mps, cuda, cpu, vulkan
--log-level LEVEL            Logging verbosity: DEBUG, INFO, WARNING, ERROR
--report-json PATH           Export structured JSON report to file
```

### Example Commands

```bash
# Process main video with yolo26x on Apple Silicon
python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" --model yolo26x --device mps

# Process all cameras with multiple models on CUDA
python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" \
  --model "yolov8x,yolo26x" --device cuda --all

# Lower confidence threshold for more detections
python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" \
  --model yolo26x --conf 0.15

# Enable debug logging and export JSON report
python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" \
  --model yolo26x --log-level DEBUG --report-json report.json
```

---

## Architecture

### Core Components

- **DetectionAgent** (`yolodetector/models/detector.py`): Model loading and inference
- **AnnotationAgent** (`yolodetector/annotation/renderer.py`): Frame rendering and visual styling
- **VideoIOAgent** (`yolodetector/video/io.py`): Video capture/write and validation
- **ReportingAgent** (`yolodetector/reporting/summary.py`): Statistics and critical findings aggregation
- **ConfigAgent** (`yolodetector/config.py`): Centralized configuration management

### Design Principles

- SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- Clean Architecture: Domain logic separated from framework details
- Dependency Injection: All agents receive config objects, not global state
- Testability: Stateless functions, clear boundaries, mockable dependencies

---

## Critical Classes

Standard COCO models include `cell phone` but NOT `glasses` or `sunglasses`.

To detect glasses:
```bash
pip install ultralytics>=8.1.0
# Use YOLO-World or custom-trained models
```

---

## Supported Platforms

### Hardware

| Platform | Environment File | GPU Support |
|----------|------------------|------------|
| Apple Silicon (M1/M2/M3) | `environment-apple-silicon.yml` | MPS |
| Intel Mac | `environment-intel-mac.yml` | None (CPU) |
| Ubuntu ARM | `environment-ubuntu-arm.yml` | CPU |
| Ubuntu CUDA | `environment-ubuntu-cuda.yml` | NVIDIA CUDA 12.1 |
| Ubuntu Vulkan | `environment-ubuntu-vulkan.yml` | Vulkan |
| Windows ARM | `environment-windows-arm.yml` | CPU |
| Windows CPU | `environment-windows-cpu.yml` | CPU |
| Windows CUDA | `environment-windows-cuda.yml` | NVIDIA CUDA 12.1 |
| Windows Vulkan | `environment-windows-vulkan.yml` | Vulkan |
| WSL2 ARM | `environment-wsl2-arm.yml` | CPU |
| WSL2 CPU | `environment-wsl2-cpu.yml` | CPU |
| WSL2 CUDA | `environment-wsl2-cuda.yml` | NVIDIA CUDA 12.1 |
| WSL2 Vulkan | `environment-wsl2-vulkan.yml` | Vulkan |
| NVIDIA DGX | `environment-dgx-spark.yml` | Multi-GPU + Spark |

---

## Performance

| Model | Parameters | Size | Speed (M3 Max) | Accuracy |
|-------|-----------|------|----------------|----------|
| yolov8n | 3.2M | 6MB | ~60 FPS | 37.3% mAP |
| yolov8s | 11.2M | 22MB | ~45 FPS | 44.9% mAP |
| yolov8x | 68.2M | 131MB | ~25 FPS | 53.9% mAP |
| yolo26x | 68M | ~130MB | ~30 FPS | 57.5% mAP |

---

## Directory Structure

```
/
├── main.py                      # Entry point
├── yolodetector/
│   ├── config.py               # Configuration models
│   ├── models/
│   │   └── detector.py         # YoloDetector class
│   ├── annotation/
│   │   └── renderer.py         # FrameAnnotator class
│   ├── video/
│   │   └── io.py               # VideoIO class
│   └── reporting/
│       └── summary.py          # ReportAggregator class
├── tests/
│   ├── conftest.py             # Shared test fixtures
│   ├── test_config.py          # Config unit tests
│   ├── test_detector.py        # Detector unit tests
│   ├── test_renderer.py        # Renderer unit tests
│   ├── test_video_io.py        # Video I/O unit tests
│   ├── test_reporter.py        # Reporter unit tests
│   └── test_integration.py     # Integration tests
├── docs/
│   ├── architecture.md         # Design and agent responsibilities
│   ├── cli-reference.md        # CLI flag reference
│   ├── configuration.md        # Configuration guide
│   ├── development.md          # Development guide
│   ├── setup.md                # Platform-specific setup
│   ├── troubleshooting.md      # Common issues and fixes
│   └── usage.md                # Usage examples
├── environment-*.yml            # Conda environment files
├── .gitignore                   # Git ignore patterns
├── Makefile                     # Development commands
├── CLAUDE.md                    # Project guidance and preferences
├── AGENTS.md                    # Agent definitions and skills
├── README.md                    # This file
└── LICENSE                      # AGPL-3.0
```

---

## License

**AGPL-3.0** — Copyright © 2026 Kinn Coelho Juliao <kinncj@gmail.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

## Documentation

Comprehensive guides are available in the `docs/` directory:

- **[Architecture Guide](docs/architecture.md)** - Design principles, agent responsibilities, and system architecture
- **[CLI Reference](docs/cli-reference.md)** - Complete command-line flag reference
- **[Configuration Guide](docs/configuration.md)** - Advanced configuration options and tuning
- **[Development Guide](docs/development.md)** - Contributing, testing, and development workflow
- **[Setup Guide](docs/setup.md)** - Platform-specific installation and environment setup
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues, solutions, and debugging tips
- **[Usage Guide](docs/usage.md)** - Detailed usage examples and workflows

For project guidance and design principles, see [CLAUDE.md](CLAUDE.md) and [AGENTS.md](AGENTS.md).

---

## Testing

Run the comprehensive test suite:

```bash
# Install dev dependencies
make install-dev

# Run all tests (47 tests)
make test

# Run specific test modules
make test-config
make test-detector
make test-annotator

# Run with coverage
make test-coverage
```

## Contributing

Contributions welcome. Follow CLAUDE.md and AGENTS.md for design guidance.

- Keep responsibilities separated
- Enforce SOLID principles
- Maintain clean architecture
- Add tests for new features (required)
- Verify with `make test` before submitting

---

## Contact

**Kinn Coelho Juliao** <kinncj@gmail.com>

---

## Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [PyTorch](https://pytorch.org/)
