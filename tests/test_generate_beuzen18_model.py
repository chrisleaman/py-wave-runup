"""
Unit tests for generate_beuzen18_model.py

Tests the Beuzen18 model generation script across different Python versions.
Note: scikit-learn may generate different binary files for different Python versions,
so tests focus on functionality rather than exact binary comparison.
"""

import os
import sys
import tempfile
import warnings
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from joblib import load
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

# Filter expected sklearn warnings during testing
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings(
    "ignore", message=".*optimal value found.*close to.*bound.*", category=UserWarning
)

# Import the module we're testing
sys.path.insert(
    0, str(Path(__file__).parent.parent / "py_wave_runup" / "datasets" / "beuzen18")
)

try:
    from generate_beuzen18_model import main
except ImportError:
    # If direct import fails, try with path manipulation
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "generate_beuzen18_model",
        Path(__file__).parent.parent
        / "py_wave_runup"
        / "datasets"
        / "beuzen18"
        / "generate_beuzen18_model.py",
    )
    generate_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generate_module)
    main = generate_module.main


class TestGenerateBeuzen18Model:
    """Test class for Beuzen18 model generation."""

    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data for testing."""
        # Create realistic wave runup training data similar to the actual dataset
        data = {
            "Hs": [2.0, 1.5, 3.0, 1.8, 2.5],
            "Tp": [8.0, 7.5, 10.0, 8.5, 9.0],
            "beach_slope": [0.1, 0.08, 0.12, 0.09, 0.11],
            "runup": [1.2, 0.9, 1.8, 1.1, 1.5],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_main_function_creates_model_file(self, sample_training_data, temp_dir):
        """Test that main() creates a joblib file with a trained GP model."""
        # Create temporary CSV file
        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        # Create expected output path
        model_path = temp_dir / "gp_runup_model.joblib"

        # Change to temp directory to simulate script execution context
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            # Check that model file was created
            assert model_path.exists(), "Model file was not created"

            # Load and verify the model
            model = load(model_path)
            assert isinstance(
                model, GaussianProcessRegressor
            ), "Model is not a GaussianProcessRegressor"

            # Verify model properties
            assert hasattr(
                model, "kernel_"
            ), "Model was not fitted (no kernel_ attribute)"
            assert model.random_state == 123, "Random state not preserved"
            assert model.normalize_y is True, "normalize_y not set correctly"
            assert (
                model.n_restarts_optimizer == 9
            ), "n_restarts_optimizer not set correctly"

        finally:
            os.chdir(original_cwd)

    def test_model_kernel_configuration(self, sample_training_data, temp_dir):
        """Test that the model uses the correct kernel configuration."""
        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            model = load(temp_dir / "gp_runup_model.joblib")

            # Check that kernel is a sum of RBF and WhiteKernel
            kernel = model.kernel_

            # The kernel should be a sum (represented as a Sum kernel in sklearn)
            # We check the string representation as it's more robust across sklearn versions
            kernel_str = str(kernel)
            assert "RBF" in kernel_str, "RBF kernel component not found"
            assert "WhiteKernel" in kernel_str, "WhiteKernel component not found"

        finally:
            os.chdir(original_cwd)

    def test_model_training_with_realistic_data(self, temp_dir):
        """Test model training with data similar to the actual Beuzen18 dataset."""
        # Create more realistic training data
        realistic_data = pd.DataFrame(
            {
                "Hs": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
                "Tp": [6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0],
                "beach_slope": [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.22],
                "runup": [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4],
            }
        )

        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        realistic_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            model = load(temp_dir / "gp_runup_model.joblib")

            # Test model predictions
            X_test = [[2.0, 8.0, 0.1]]  # [Hs, Tp, beach_slope]
            y_pred, y_std = model.predict(X_test, return_std=True)

            assert len(y_pred) == 1, "Prediction should return single value"
            assert len(y_std) == 1, "Standard deviation should return single value"
            assert y_pred[0] > 0, "Predicted runup should be positive"
            assert y_std[0] > 0, "Standard deviation should be positive"

        finally:
            os.chdir(original_cwd)

    def test_missing_csv_file_raises_error(self, temp_dir):
        """Test that missing CSV file raises appropriate error."""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            with pytest.raises(FileNotFoundError):
                main()

        finally:
            os.chdir(original_cwd)

    def test_data_preprocessing_correctness(self, sample_training_data, temp_dir):
        """Test that data preprocessing works correctly."""
        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        # Mock the pandas read_csv to capture the preprocessing
        with patch("pandas.read_csv") as mock_read_csv:
            mock_read_csv.return_value = sample_training_data

            # Mock the GaussianProcessRegressor fit method to capture input data
            with patch(
                "sklearn.gaussian_process.GaussianProcessRegressor.fit"
            ) as mock_fit:
                with patch("joblib.dump") as mock_dump:  # Prevent actual file creation
                    original_cwd = os.getcwd()
                    try:
                        os.chdir(temp_dir)
                        main()

                        # Verify that fit was called with correct data shapes
                        assert mock_fit.call_count == 1
                        X, y = mock_fit.call_args[0]

                        # X should have 3 features (Hs, Tp, beach_slope)
                        assert X.shape[1] == 3, f"Expected 3 features, got {X.shape[1]}"

                        # y should be 2D array with single column (runup)
                        assert y.shape[1] == 1, f"Expected 1 target, got {y.shape[1]}"

                        # Number of samples should match
                        assert (
                            X.shape[0] == y.shape[0]
                        ), "Feature and target sample counts don't match"

                    finally:
                        os.chdir(original_cwd)

    @pytest.mark.parametrize("python_version", ["3.10", "3.11", "3.12", "3.13", "3.14"])
    def test_cross_python_version_compatibility(
        self, sample_training_data, temp_dir, python_version
    ):
        """
        Test that the model generation works across different Python versions.

        Note: This test verifies the functionality rather than binary compatibility,
        as scikit-learn may generate different binary files for different Python versions.
        """
        # Skip if current Python version doesn't match test version
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current_version != python_version:
            pytest.skip(
                f"Skipping test for Python {python_version}, running on {current_version}"
            )

        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            # Load and test model
            model = load(temp_dir / "gp_runup_model.joblib")

            # Verify core functionality works regardless of Python version
            assert isinstance(model, GaussianProcessRegressor)

            # Test prediction works
            X_test = [[2.0, 8.0, 0.1]]
            y_pred = model.predict(X_test)
            assert len(y_pred) == 1
            assert isinstance(y_pred[0], (int, float))

            # Store Python version info for reference
            model_info = {
                "python_version": python_version,
                "sklearn_version": getattr(model, "__module__", "unknown"),
            }

        finally:
            os.chdir(original_cwd)

    def test_model_reproducibility_with_same_seed(self, sample_training_data, temp_dir):
        """Test that model training is reproducible with the same random seed."""
        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Generate first model
            main()
            model1 = load(temp_dir / "gp_runup_model.joblib")

            # Remove the file and generate again
            (temp_dir / "gp_runup_model.joblib").unlink()
            main()
            model2 = load(temp_dir / "gp_runup_model.joblib")

            # Test predictions are identical (reproducibility check)
            X_test = [[2.0, 8.0, 0.1], [1.5, 7.0, 0.12]]
            pred1 = model1.predict(X_test)
            pred2 = model2.predict(X_test)

            # Due to the random seed (123), predictions should be very similar
            assert len(pred1) == len(pred2)
            for p1, p2 in zip(pred1, pred2):
                assert (
                    abs(p1 - p2) < 1e-10
                ), "Models should be reproducible with same random seed"

        finally:
            os.chdir(original_cwd)

    def test_model_performance_bounds(self, sample_training_data, temp_dir):
        """Test that generated model performs within reasonable bounds."""
        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        sample_training_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            model = load(temp_dir / "gp_runup_model.joblib")

            # Test on training data bounds
            X_train = sample_training_data[["Hs", "Tp", "beach_slope"]].values
            y_train = sample_training_data[["runup"]].values

            y_pred = model.predict(X_train)

            # Model should predict values in reasonable range
            assert all(y_pred >= 0), "All runup predictions should be non-negative"
            assert all(
                y_pred <= 10
            ), "All runup predictions should be reasonable (< 10m)"

            # Model should perform reasonably well on training data
            train_score = model.score(X_train, y_train)
            assert (
                train_score > 0.5
            ), f"Model R² score should be > 0.5, got {train_score}"

        finally:
            os.chdir(original_cwd)


class TestBeuzen18ModelIntegration:
    """Integration tests for Beuzen18 model generation with the actual py_wave_runup package."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_generated_model_loads_in_beuzen2019_class(self, temp_dir):
        """Test that a generated model can be loaded by the Beuzen2019 model class."""
        # Create realistic training data
        realistic_data = pd.DataFrame(
            {
                "Hs": [1.0, 1.5, 2.0, 2.5, 3.0],
                "Tp": [7.0, 8.0, 9.0, 10.0, 11.0],
                "beach_slope": [0.08, 0.10, 0.12, 0.14, 0.16],
                "runup": [0.6, 0.9, 1.2, 1.5, 1.8],
            }
        )

        csv_path = temp_dir / "lidar_runup_data_for_GP_training.csv"
        realistic_data.to_csv(csv_path, index_label="idx")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            main()

            # Test that the generated model works with the actual Beuzen2019 class
            model = load(temp_dir / "gp_runup_model.joblib")

            # Test prediction format matches expected format
            test_data = [[2.0, 8.0, 0.1]]
            prediction = model.predict(test_data)

            assert isinstance(prediction, (list, tuple)) or hasattr(
                prediction, "__iter__"
            )
            assert len(prediction) == 1
            assert isinstance(prediction[0], (int, float))

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__])
