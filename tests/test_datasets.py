from pytest import approx, raises

from py_wave_runup import datasets
from py_wave_runup.data.beuzen18.generate_beuzen18_model import train_model


class TestPower18(object):
    def test_load_data(self):
        df = datasets.load_power18()
        first_row = {
            "dataset": "ATKINSON2017",
            "beach": "AUSTINMER",
            "case": "AU24-1",
            "lab_field": "F",
            "hs": 0.739476577,
            "tp": 6.4,
            "beta": 0.102,
            "d50": "0.000445",
            "roughness": 0.0011125,
            "r2": 1.979,
        }
        assert first_row == df.iloc[0].to_dict()


class TestBeuzen18Dataset(object):
    def test_data_training(self):
        train_model(save_model=False)
