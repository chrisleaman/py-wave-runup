"""
This module is an interface for loading existing wave runup datasets. These datasets
can be used to evaluate existing models or train new models. Datasets are returned as
pandas dataframes.
"""

import pandas as pd
import io
import pkgutil


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
