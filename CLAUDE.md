# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package called `py-wave-runup` that implements empirical wave runup models for coastal engineers and scientists. Wave runup refers to the final part of a wave's journey as it travels from offshore onto the beach, comprising:

- **setup**: time averaged superelevation of mean water level above SWL
- **swash**: time varying fluctuation of instantaneous water level about setup elevation

## Architecture

The codebase is organized into several key modules:

- **`py_wave_runup/models.py`**: Core module containing empirical wave runup models (Stockdon2006, Power2018, Holman1986, Nielsen2009, etc.). All models inherit from abstract `RunupModel` base class with parameters Hs (significant wave height), Tp (peak wave period), beta (beach slope), and optional Lp, h, r.

- **`py_wave_runup/ensembles.py`**: Ensemble techniques to combine predictions from multiple models, starting with `EnsembleRaw` base class.

- **`py_wave_runup/datasets.py`**: Interface for loading wave runup datasets as pandas DataFrames for model evaluation and training. Uses scikit-learn preprocessing and custom Perlin noise utilities.

- **`py_wave_runup/utils.py`**: Utility functions including `PerlinNoise` for synthetic data generation.

## Development Commands

### Environment Setup
- **uv with existing venv**: `uv sync --active` (uses C:\Users\Chris\venv\py-wave-runup)
- **uv with dev dependencies**: `uv sync --active --dev` (includes development dependencies)
- **Alternative**: `pip install -e ".[dev]"` (if not using uv)

**Note**: The preferred virtual environment location is `C:\Users\Chris\venv\py-wave-runup`. Use `--active` flag to target this environment.

### Testing
- **Run all tests**: `uv run --active pytest`
- **Run with coverage**: `uv run --active pytest --cov=py_wave_runup --cov-report term-missing`
- **Run doctests**: Tests include doctests via `--doctest-modules` flag

### Code Quality
- **Pre-commit hooks**: `uv run --active pre-commit install` then `uv run --active pre-commit run -a`
- **Black formatting**: `uv run --active black .`

### Documentation
- **Build docs**: `uv run --active sphinx-build -M html ".\docs" ".\docs\_build"`
- **Documentation hosted at**: https://py-wave-runup.readthedocs.io

### Build and Publishing
- **Build package**: `uv build`
- **Build wheel only**: `uv build --wheel`
- **Publish to PyPI**: `uv publish`
- **Publish to Test PyPI**: `uv publish --publish-url https://test.pypi.org/legacy/`
- **Check package**: `uv run --active twine check dist/*`

### Dependencies
- **Core**: numpy>=1.24, pandas>=2.0, joblib>=1.3, scikit-learn>=1.3
- **Dev**: pytest, black, sphinx, coverage, pre-commit, matplotlib
- **Python**: 3.10+ (supports up to 3.14)
- **Build system**: Uses hatchling backend with uv package manager

## Key Models Available

The package implements 9+ empirical wave runup models including Stockdon2006 (most widely used), Power2018 (Gene-Expression Programming), Beuzen2019 (Gaussian Process), and others. Each model accepts offshore wave conditions and returns runup predictions via properties like `R2`, `setup`, `sinc`, `sig`.