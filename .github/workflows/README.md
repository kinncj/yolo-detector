# GitHub Actions Workflows

This directory contains CI/CD workflows for automated testing and quality checks.

## Workflows

### 1. `test.yml` - Cross-platform Test Suite
**Triggers:** Push to main/develop, Pull Requests, Manual dispatch

**Matrix:**
- OS: Ubuntu, macOS, Windows
- Python: 3.10, 3.11

**Steps:**
1. Checkout code
2. Set up Conda environment
3. Install dependencies (requirements.txt + pytest)
4. Run test suite (47 tests)
5. Generate coverage report (Ubuntu + Python 3.11 only)
6. Upload coverage to Codecov

**Badge:**
```markdown
[![Tests](https://github.com/kinncj/yolo-detector/actions/workflows/test.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/test.yml)
```

---

### 2. `lint.yml` - Code Quality Checks
**Triggers:** Push to main/develop, Pull Requests, Manual dispatch

**Checks:**
- Black (code formatting)
- isort (import sorting)
- Pylint (code linting)
- Mypy (type checking)
- Bandit (security analysis)

**Badge:**
```markdown
[![Lint](https://github.com/kinncj/yolo-detector/actions/workflows/lint.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/lint.yml)
```

---

### 3. `ci.yml` - Complete CI Pipeline
**Triggers:** Push to main/develop, Pull Requests, Manual dispatch

**Steps:**
1. Format checking (black + isort)
2. Linting (pylint)
3. Test suite with coverage
4. Security checks (bandit)
5. Upload artifacts (coverage report, security report)

**Badge:**
```markdown
[![CI](https://github.com/kinncj/yolo-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/kinncj/yolo-detector/actions/workflows/ci.yml)
```

---

## Local Testing

Test the workflows locally before pushing:

### Run tests (simulates test.yml)
```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-benchmark

# Run tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=yolodetector --cov-report=term
```

### Check formatting (simulates lint.yml)
```bash
# Install dev tools
pip install black isort pylint mypy bandit safety

# Check formatting
black --check yolodetector/ main.py tests/ --line-length=120
isort --check yolodetector/ main.py tests/ --profile=black --line-length=120

# Run linter
pylint yolodetector/ main.py --max-line-length=120
```

### Complete CI check (simulates ci.yml)
```bash
make ci
```

---

## Conda Environment Considerations

All workflows use `conda-incubator/setup-miniconda@v3` to ensure consistent environment setup across platforms:

- **Miniforge**: Uses Mambaforge for faster dependency resolution
- **Mamba**: Enabled for faster package installation
- **Python versions**: Tests against 3.10 and 3.11
- **Shell**: Uses `bash -l {0}` to activate conda environment in each step

This mirrors the local conda environment setup from the project's environment YAML files.

---

## Troubleshooting

### Workflow fails on dependency installation
- Check that `requirements.txt` is up to date
- Verify conda environment activation in workflow

### Tests pass locally but fail in CI
- Check Python version differences (3.10 vs 3.11)
- Check OS-specific behavior (path separators, line endings)
- Review workflow logs in GitHub Actions tab

### Coverage upload fails
- Ensure Codecov token is set in repository secrets (optional for public repos)
- Check `codecov/codecov-action` version compatibility

---

## Updating Workflows

1. Edit workflow files in `.github/workflows/`
2. Test locally using commands above
3. Commit and push to trigger workflow
4. Monitor in GitHub Actions tab
5. Check status badges in README

---

## Required Secrets

For full functionality, configure these secrets in your GitHub repository:

- `CODECOV_TOKEN` (optional for public repos) - For coverage uploads

**Setup:** Repository Settings → Secrets and variables → Actions → New repository secret
