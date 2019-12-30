"""
This module is an interface for loading existing wave runup datasets. These datasets
can be used to evaluate existing models or train new models. Datasets are returned as
:obj:`pandas.DataFrame`.
"""

import pandas as pd
import io
import pkgutil
from datetime import datetime, timedelta
import random
from sklearn.preprocessing import minmax_scale
from py_wave_runup import models
import numpy as np

from py_wave_runup.utils import PerlinNoise


def load_power18():
    """
        This function loads the supplementary data from:

            Power, H.E., Gharabaghi, B., Bonakdari, H., Robertson, B., Atkinson, A.L.,
            Baldock, T.E., 2018. Prediction of wave runup on beaches using
            Gene-Expression Programming and empirical relationships. Coastal Engineering.
            https://doi.org/10.1016/j.coastaleng.2018.10.006

        Examples:
            >>> from py_wave_runup import datasets
            >>> df = datasets.load_power18()
            >>> df.describe()
                            hs           tp         beta    roughness           r2
            count  1390.000000  1390.000000  1390.000000  1390.000000  1390.000000
            mean      1.893131     9.227035     0.120612     0.024779     2.318814
            std       1.309243     3.589004     0.062236     0.043617     1.776918
            min       0.018576     0.805805     0.009000     0.000003     0.027336
            25%       0.895942     7.517556     0.088228     0.001000     1.103500
            50%       1.848050     9.963089     0.108422     0.003750     1.923500
            75%       2.391756    10.995500     0.129220     0.007500     3.406660
            max       7.174100    23.680333     0.286551     0.125000    12.669592

    """

    # To load a resource in a package, need to use pkgutil.
    # Refer https://stackoverflow.com/a/6028106
    data = pkgutil.get_data(__name__, "datasets/power18.csv")

    # Manually define names for each column
    names = [
        "dataset",
        "beach",
        "case",
        "lab_field",
        "hs",
        "tp",
        "beta",
        "d50",
        "roughness",
        "r2",
    ]

    # Need to use the io package to read in the .csv
    # Refer to https://stackoverflow.com/a/20697069
    df = pd.read_csv(io.BytesIO(data), encoding="utf8", names=names, skiprows=1)

    return df


def generate_random_stockdon_ts(
    seed=12345,
    t_start=datetime(2000, 1, 1),
    t_end=datetime(2000, 1, 2),
    dt=timedelta(hours=1),
    hs_range=(1, 3),
    tp_range=(6, 10),
    beta_range=(0.08, 0.1),
    noise_std=0.3,
):
    """
    Generates a random timeseries of wave parameters and runup values

    Examples:
        Get a randomly generated dataframe of wave parameters and noisey runup values.

    >>> from py_wave_runup import datasets
    >>> df = datasets.generate_random_stockdon_ts()
    >>> df.head()
                               hs        tp      beta  ...     swash       sig      sinc
    2000-01-01 00:00:00  3.000000  6.000000  0.098110  ...  1.171474  0.717714  0.894084
    2000-01-01 01:00:00  2.850109  6.128432  0.099052  ...  1.378190  0.919351  1.104072
    2000-01-01 02:00:00  2.865462  6.461471  0.099766  ...  1.154970  0.664189  0.866796
    2000-01-01 03:00:00  2.942888  6.750824  0.100000  ...  1.223142  0.701520  0.918580
    2000-01-01 04:00:00  2.906808  6.937742  0.099069  ...  2.001251  1.476527  1.687905
    <BLANKLINE>
    [5 rows x 8 columns]
    """

    # Create the time index for our dataframe
    index = pd.date_range(start=t_start, end=t_end, freq=dt)
    df = pd.DataFrame(index=index)

    # Create some random noise
    random.seed(seed)
    np.random.seed(seed)
    pn = PerlinNoise(num_octaves=7, persistence=0.5)

    # Generate input parameters. Note that we offset the noise value by the length of
    # the index to avoid having the same timeseries shape for each parameter.
    l = len(index)
    hs = minmax_scale([pn.noise(i) for i, _ in enumerate(index)], hs_range)
    tp = minmax_scale([pn.noise(i + l) for i, _ in enumerate(index)], tp_range)
    beta = minmax_scale([pn.noise(i + 2 * l) for i, _ in enumerate(index)], beta_range)

    # Generate wave parameters based on Stockdon
    model = models.Stockdon2006(Hs=hs, Tp=tp, beta=beta)

    # Generate additional noise
    noise = np.random.normal(0, noise_std, l)

    # Combine into a dataframe
    df["hs"] = hs
    df["tp"] = tp
    df["beta"] = beta
    df["r2"] = model.R2 + noise
    df["setup"] = model.setup + noise
    df["swash"] = model.swash + noise
    df["sig"] = model.sig + noise
    df["sinc"] = model.sinc + noise

    return df


if __name__ == "__main__":
    generate_stockdon_ts()
