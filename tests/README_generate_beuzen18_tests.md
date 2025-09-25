# Beuzen18 Model Generation Tests

## Overview

The tests in `test_generate_beuzen18_model.py` verify the functionality of the `generate_beuzen18_model.py` script across different Python versions (3.10-3.14) as specified in the project's test matrix.

## Key Testing Considerations

### Python Version Compatibility
- **Different scikit-learn binaries**: scikit-learn may generate different binary files for different Python versions due to underlying changes in NumPy, pickle protocols, or sklearn internals.
- **Functional equivalence**: Tests focus on verifying that the generated models produce functionally equivalent results rather than identical binary files.
- **Version-specific skipping**: Tests automatically skip for Python versions not currently running to avoid false failures.

### Test Categories

#### 1. Core Functionality Tests
- `test_main_function_creates_model_file`: Verifies basic model file creation
- `test_model_kernel_configuration`: Ensures correct RBF + WhiteKernel setup
- `test_missing_csv_file_raises_error`: Error handling for missing input data

#### 2. Data Processing Tests
- `test_data_preprocessing_correctness`: Validates input/output data shapes
- `test_model_training_with_realistic_data`: Tests with realistic wave runup data

#### 3. Cross-Version Compatibility
- `test_cross_python_version_compatibility`: Parametrized test for Python 3.10-3.14
- Tests functional equivalence across versions
- Skips gracefully when version doesn't match current interpreter

#### 4. Quality Assurance Tests
- `test_model_reproducibility_with_same_seed`: Ensures deterministic behavior
- `test_model_performance_bounds`: Validates reasonable prediction ranges
- `test_generated_model_loads_in_beuzen2019_class`: Integration with main package

## Running Tests Across Python Versions

### Using the justfile
```bash
# Test current Python version only
just test

# Test across all supported Python versions
just test-matrix

# Test specific Python version
just test-py 3.11
```

### Manual Testing
```bash
# Test with specific Python version
uv run --python 3.11 --isolated pytest tests/test_generate_beuzen18_model.py -v

# Test with current environment
uv run --active pytest tests/test_generate_beuzen18_model.py -v
```

## Expected Behavior by Python Version

| Python Version | Expected Result | Notes |
|---|---|---|
| 3.10 | ✅ All tests pass | Base version for development |
| 3.11 | ✅ All tests pass | Should work identically |
| 3.12 | ✅ All tests pass | May have minor sklearn differences |
| 3.13 | ✅ All tests pass | Newer sklearn/numpy versions |
| 3.14 | ✅ All tests pass | Latest supported version |

## Warnings and Expected Issues

### Normal Warnings
- `ConvergenceWarning`: sklearn may warn about kernel parameter optimization - this is normal for small test datasets
- `UserWarning`: sklearn may warn about feature names - acceptable for test data

### Version-Specific Considerations
- **Binary compatibility**: Models trained on different Python versions may not be directly interchangeable
- **Sklearn version differences**: Minor differences in optimization algorithms across sklearn versions
- **NumPy changes**: Underlying numerical operations may vary slightly between Python versions

## Maintenance Notes

When adding new Python version support:
1. Update `pyproject.toml` classifiers
2. Update `justfile` test-matrix
3. Add new version to the parametrized test
4. Verify all tests pass on the new version

When sklearn is updated:
1. Regenerate the `gp_runup_model.joblib` file for each supported Python version
2. Run full test suite to ensure compatibility
3. Update test expectations if sklearn API changes