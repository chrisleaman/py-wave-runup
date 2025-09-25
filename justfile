# py-wave-runup justfile
# Run `just` to see all available commands

# Default recipe - show help
default:
    @just --list

# === Environment Setup ===

# Set up development environment with uv
setup:
    uv sync --active --dev

# Set up development environment with pip (alternative)
setup-pip:
    pip install -e ".[dev]"

# Code formatting and linting setup
hooks:
    @echo "Pre-commit hooks removed - use 'just format' and 'just lint' manually"

# === Testing ===

# Run all tests
test:
    uv run --active pytest

# Run tests with coverage report
test-cov:
    uv run --active pytest --cov=py_wave_runup --cov-report term-missing

# Run tests with coverage and generate HTML report
test-html:
    uv run --active pytest --cov=py_wave_runup --cov-report html

# Run doctests only
doctest:
    uv run --active pytest --doctest-modules py_wave_runup/

# Run tests with all checks (comprehensive testing)
test-all: format lint test docs

# Test across multiple Python versions using uv
test-matrix:
    @echo "Testing across Python 3.10, 3.11, 3.12, 3.13, 3.14..."
    @echo "=========================================="
    @echo "Testing Python 3.10..."
    uv run --python 3.10 --isolated pytest --tb=short || echo "Python 3.10 failed"
    @echo "=========================================="
    @echo "Testing Python 3.11..."
    uv run --python 3.11 --isolated pytest --tb=short || echo "Python 3.11 failed"
    @echo "=========================================="
    @echo "Testing Python 3.12..."
    uv run --python 3.12 --isolated pytest --tb=short || echo "Python 3.12 failed"
    @echo "=========================================="
    @echo "Testing Python 3.13..."
    uv run --python 3.13 --isolated pytest --tb=short || echo "Python 3.13 failed"
    @echo "=========================================="
    @echo "Testing Python 3.14..."
    uv run --python 3.14 --isolated pytest --tb=short || echo "Python 3.14 failed"
    @echo "=========================================="
    @echo "Multi-version testing complete!"

# Test a specific Python version
test-py version:
    @echo "Testing with Python {{version}}..."
    uv run --python {{version}} --isolated pytest

# === Code Quality ===

# Lint/check code formatting with black (no modifications)
lint:
    uv run --active black --check .

# Format code with black
format:
    uv run --active black .

# === Documentation ===

# Build documentation
docs:
    uv run --active sphinx-build -M html ".\docs" ".\docs\_build"

# Build docs and open in browser (Windows)
docs-open: docs
    start ".\docs\_build\html\index.html"

# Clean documentation build
docs-clean:
    uv run --active sphinx-build -M clean ".\docs" ".\docs\_build"

# === Building and Publishing ===

# Build the package
build:
    uv build

# Build wheel only
build-wheel:
    uv build --wheel

# Check the built package
check:
    uv run --active twine check dist/*

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info/
    rm -rf docs/_build/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -delete

# Publish to Test PyPI
publish-test: build check
    uv publish --publish-url https://test.pypi.org/legacy/

# Publish to PyPI (production)
publish: build check
    uv publish

# === Development Workflow ===

# Full development setup (environment + hooks)
dev-setup: setup hooks
    @echo "Development environment ready!"

# Quick development check (format, lint, test)
check-all: format lint test

# Prepare for release (full test suite, docs, build)
release-prep: test-all docs build check
    @echo "Ready for release!"

# === Utilities ===

# Show project info
info:
    @echo "py-wave-runup - Empirical wave runup models in Python"
    @echo "Python version: $(python --version)"
    @echo "UV version: $(uv --version)"
    @echo "Active environment: $(which python)"

# Update dependencies
update:
    uv sync --active --dev --upgrade