# YOLO DETECTOR - Makefile
# Quick commands for common development tasks

.PHONY: help install test lint format clean run docker

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "YOLO DETECTOR - Development Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	python -c 'from ultralytics import YOLO; YOLO("yolo26x.pt"); print("✓ Models ready")'

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-benchmark black isort pylint mypy bandit safety

test: ## Run all tests
	pytest tests/ -v --tb=short

test-detector: ## Test DetectionAgent
	pytest tests/test_detector.py -v

test-annotator: ## Test AnnotationAgent
	pytest tests/test_renderer.py -v

test-video: ## Test VideoIOAgent
	pytest tests/test_video_io.py -v

test-reporter: ## Test ReportingAgent
	pytest tests/test_reporter.py -v

test-config: ## Test ConfigAgent
	pytest tests/test_config.py -v

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=yolodetector --cov-report=html --cov-report=term

test-integration: ## Run integration tests
	pytest tests/test_integration.py -v

lint: ## Run linting checks
	pylint yolodetector/ main.py --max-line-length=120

lint-strict: ## Run strict linting
	pylint yolodetector/ main.py --max-line-length=120 --fail-under=8.0

format: ## Format code with black and isort
	black yolodetector/ main.py tests/ --line-length=120
	isort yolodetector/ main.py tests/ --profile=black --line-length=120

format-check: ## Check formatting without changes
	black --check yolodetector/ main.py tests/ --line-length=120
	isort --check yolodetector/ main.py tests/ --profile=black --line-length=120

typecheck: ## Run mypy type checking
	mypy yolodetector/ main.py --ignore-missing-imports

security: ## Run security checks
	bandit -r yolodetector/ -f json -o bandit-report.json
	safety check

clean: ## Clean cache and output files
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf output/
	rm -rf kinn_test/output/

run: ## Run detection on test data
	python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" --model yolo26x

run-multi: ## Run multi-model comparison
	python main.py --input-dir kinn_test --prefix "2026-02-04 11-42-16" --model "yolov8x,yolo26x,yolo12x"

benchmark: ## Run performance benchmarks
	pytest tests/ --benchmark-only

docker-build-cuda: ## Build Docker image (CUDA)
	docker build -f Dockerfile.cuda -t yolodetector:cuda .

docker-build-cpu: ## Build Docker image (CPU)
	docker build -f Dockerfile.cpu -t yolodetector:cpu .

docker-run-cuda: ## Run Docker container (CUDA)
	docker run --gpus all -v $(PWD)/videos:/workspace/videos yolodetector:cuda python main.py --input-dir /workspace/videos --device cuda

docker-run-cpu: ## Run Docker container (CPU)
	docker run -v $(PWD)/videos:/workspace/videos yolodetector:cpu python main.py --input-dir /workspace/videos --device cpu

docs: ## Build documentation
	@echo "Documentation available in docs/ directory"
	@echo "- docs/ARCHITECTURE.md"
	@echo "- docs/SETUP.md"
	@echo "- docs/USAGE.md"
	@echo "- docs/TROUBLESHOOTING.md"

all: format lint test ## Run format, lint, and tests

ci: format-check lint test-coverage ## Run CI checks (format, lint, coverage)
