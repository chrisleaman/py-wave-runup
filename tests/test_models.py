from py_wave_runup import models
import pytest


class TestStockdon2006(object):
    def test_reflective(self):
        model = models.Stockdon2006(Hs=4, Tp=11, beta=0.1)
        assert model.R2 == pytest.approx(2.54, 0.1)
        assert model.setup == pytest.approx(0.96, 0.1)

    def test_dissipative(self):
        model = models.Stockdon2006(Hs=4, Tp=11, beta=0.001)
        assert model.R2 == pytest.approx(1.18, 0.1)
        assert model.setup == pytest.approx(0.0096, 0.1)

    def test_no_wave_length(self):
        with pytest.raises(ValueError):
            models.Stockdon2006(Hs=4, beta=0.1)

    def test_wave_length(self):
        model = models.Stockdon2006(Hs=4, Lp=200, beta=0.05)
        assert model.R2 == pytest.approx(1.69, 0.1)

    def test_list_input(self):
        model = models.Stockdon2006(Hs=[1, 2], Lp=[100, 200], beta=[0.05, 0.1])

        for result, expected in zip(model.R2, [0.59, 1.84]):
            assert result == pytest.approx(expected, 0.1)

        for result, expected in zip(model.setup, [0.175, 0.7]):
            assert result == pytest.approx(expected, 0.1)
