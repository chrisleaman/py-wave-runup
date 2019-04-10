from py_wave_runup import models
import pytest


class TestStockdon2006(object):
    def test_reflective(self):
        model = models.Stockdon2006(Hs=4, Tp=11, beta=0.1)
        assert model.R2 == pytest.approx(2.54, abs=0.01)
        assert model.setup == pytest.approx(0.96, abs=0.01)
        assert model.sig == pytest.approx(1.65, abs=0.01)
        assert model.sinc == pytest.approx(2.06, abs=0.01)

    def test_dissipative(self):
        model = models.Stockdon2006(Hs=4, Tp=11, beta=0.001)
        assert model.R2 == pytest.approx(1.18, abs=0.01)
        assert model.setup == pytest.approx(0.0096, abs=0.01)
        assert model.sig == pytest.approx(1.65, abs=0.01)
        assert model.sinc == pytest.approx(0.02, abs=0.01)

    def test_wave_length(self):
        model = models.Stockdon2006(Hs=4, Lp=200, beta=0.05)
        assert model.R2 == pytest.approx(1.69, 0.1)

    def test_list_input(self):
        model = models.Stockdon2006(Hs=[1, 2], Lp=[100, 200], beta=[0.05, 0.1])
        assert model.R2 == pytest.approx((0.59, 1.84), abs=0.1)
        assert model.setup == pytest.approx((0.17, 0.70), abs=0.1)
        assert model.sig == pytest.approx((0.6, 1.2), abs=0.1)
        assert model.sinc == pytest.approx((0.37, 1.5), abs=0.1)

    def test_no_wave_length(self):
        with pytest.raises(ValueError):
            models.Stockdon2006(Hs=4, beta=0.1)
