from py_wave_runup import ensembles
from pytest import raises, approx


class TestEnsembleRaw(object):
    def test_invalid_param(self):
        ensemble = ensembles.EnsembleRaw(Hs=1, Tp=8, beta=0.1)
        with raises(ValueError):
            ensemble.estimate("not_r2")
