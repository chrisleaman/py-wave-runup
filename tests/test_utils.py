import numpy as np
import pandas as pd
import pytest
from pytest import approx

from py_wave_runup import utils


class TestPerlinNoise:
    def test_perlin_noise_init(self):
        noise = utils.PerlinNoise(num_octaves=4, persistence=0.5)
        assert noise.num_octaves == 4
        assert len(noise.octaves) == 4
        assert len(noise.frequencies) == 4
        assert len(noise.amplitudes) == 4

    def test_perlin_noise_generation(self):
        noise = utils.PerlinNoise(num_octaves=4, persistence=0.5)
        result = noise.noise(0.5)
        assert isinstance(result, float)

    def test_perlin_noise_octave(self):
        octave = utils.PerlinNoiseOctave()
        result = octave.noise(0.5, 0.188)
        assert isinstance(result, float)

    def test_perlin_noise_octave_methods(self):
        octave = utils.PerlinNoiseOctave()

        # Test lerp method
        lerp_result = octave.lerp(0.5, 0.0, 1.0)
        assert lerp_result == 0.5

        # Test fade method
        fade_result = octave.fade(0.5)
        assert isinstance(fade_result, float)

        # Test grad method
        grad_result = octave.grad(15, 0.5)
        assert isinstance(grad_result, float)


class TestCalculateLo:
    def test_calculate_lo_basic(self):
        df = pd.DataFrame({"Tp": [10.0, 12.0]})
        result = utils.calculate_Lo(df)

        expected = (9.81 * df.Tp * df.Tp) / (2.0 * np.pi)
        pd.testing.assert_series_equal(result, expected)

    def test_calculate_lo_single_value(self):
        df = pd.DataFrame({"Tp": [10.0]})
        result = utils.calculate_Lo(df)

        expected_value = (9.81 * 10.0 * 10.0) / (2.0 * np.pi)
        assert result.iloc[0] == approx(expected_value)


class TestReverseShoalIntermediate:
    def test_reverse_shoal_intermediate_valid(self):
        # Create test data that satisfies intermediate water conditions
        # 1/50 * Lo < water_depth < 1/2 * Lo

        water_depth = pd.Series([5.0])
        Lo = pd.Series([200.0])  # Lo = 200m, so 1/50*Lo = 4m, 1/2*Lo = 100m
        Tp = pd.Series([11.28])  # Approximately correct for Lo=200
        Hs = pd.Series([2.0])

        result = utils.reverse_shoal_intermediate(
            waterDepthSeries=water_depth, LoSeries=Lo, TpSeries=Tp, HsSeries=Hs
        )

        assert isinstance(result, pd.Series)
        assert len(result) == 1
        assert result.iloc[0] > 0  # Should be positive

    def test_reverse_shoal_intermediate_deep_water_error(self):
        # Test error condition: deep water waves (water_depth > 1/2 * Lo)
        water_depth = pd.Series([150.0])  # > 1/2 * 200 = 100
        Lo = pd.Series([200.0])
        Tp = pd.Series([11.28])
        Hs = pd.Series([2.0])

        with pytest.raises(ValueError, match="Deep water waves detected"):
            utils.reverse_shoal_intermediate(
                waterDepthSeries=water_depth, LoSeries=Lo, TpSeries=Tp, HsSeries=Hs
            )

    def test_reverse_shoal_intermediate_shallow_water_warning(self, capsys):
        # Test warning condition: shallow water waves (water_depth < 1/50 * Lo)
        water_depth = pd.Series([2.0])  # < 1/50 * 200 = 4
        Lo = pd.Series([200.0])
        Tp = pd.Series([11.28])
        Hs = pd.Series([2.0])

        # This should print a warning but not raise an error
        result = utils.reverse_shoal_intermediate(
            waterDepthSeries=water_depth, LoSeries=Lo, TpSeries=Tp, HsSeries=Hs
        )

        # Check that error message was printed
        captured = capsys.readouterr()
        assert "ERROR: Shallow water waves detected" in captured.out

        # The function should still return results
        assert isinstance(result, pd.Series)


class TestDetermineWaveDepth:
    def test_determine_wave_depth_all_conditions(self):
        df = pd.DataFrame(
            {
                "water_depth": [2.0, 10.0, 150.0],  # shallow, intermediate, deep
                "Lo": [200.0, 200.0, 200.0],
            }
        )

        result = utils.determine_waveDepth(df)

        expected = ["shallow", "intermediate", "deep"]
        assert list(result) == expected

    def test_determine_wave_depth_edge_cases(self):
        df = pd.DataFrame(
            {"water_depth": [4.0, 100.0], "Lo": [200.0, 200.0]}  # Exactly at boundaries
        )

        result = utils.determine_waveDepth(df)

        # 4.0 = 1/50 * 200, so should be intermediate
        # 100.0 = 1/2 * 200, so should be intermediate
        expected = ["intermediate", "intermediate"]
        assert list(result) == expected

    def test_determine_wave_depth_unknown_default(self):
        # Test the default value for edge case
        df = pd.DataFrame({"water_depth": [np.nan], "Lo": [200.0]})

        result = utils.determine_waveDepth(df)

        # Should handle NaN gracefully
        assert len(result) == 1


class TestReverseShoal:
    def test_reverse_shoal_intermediate_water(self):
        # Test with intermediate water only
        df = pd.DataFrame(
            {
                "water_depth": [10.0],
                "Lo": [200.0],
                "Tp": [11.28],
                "Hs": [2.0],
                "wave_depth": ["intermediate"],
            }
        )

        result = utils.reverse_shoal(df)

        # Should return a valid result
        assert len(result) == 1
        assert not np.isnan(result[0])
        assert result[0] > 0

    def test_reverse_shoal_mixed_conditions(self):
        df = pd.DataFrame(
            {
                "water_depth": [2.0, 10.0, 150.0],
                "Lo": [200.0, 200.0, 200.0],
                "Tp": [11.28, 11.28, 11.28],
                "Hs": [2.0, 2.0, 2.0],
                "wave_depth": ["shallow", "intermediate", "deep"],
            }
        )

        result = utils.reverse_shoal(df)

        # Should handle mixed conditions appropriately
        assert len(result) == 3
        assert np.isnan(result[0])  # shallow -> NaN
        assert not np.isnan(result[1])  # intermediate -> calculated value
        assert result[2] == 2.0  # deep -> Hs

    def test_reverse_shoal_deep_only(self):
        df = pd.DataFrame(
            {
                "water_depth": [150.0],
                "Lo": [200.0],
                "Tp": [11.28],
                "Hs": [2.0],
                "wave_depth": ["deep"],
            }
        )

        result = utils.reverse_shoal(df)

        # For deep water, Ho should equal Hs
        assert result[0] == 2.0

    def test_reverse_shoal_shallow_only(self):
        df = pd.DataFrame(
            {
                "water_depth": [2.0],
                "Lo": [200.0],
                "Tp": [11.28],
                "Hs": [2.0],
                "wave_depth": ["shallow"],
            }
        )

        result = utils.reverse_shoal(df)

        # Should return NaN for shallow water
        assert np.isnan(result[0])
