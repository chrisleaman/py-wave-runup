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
            >>> df.head()
                        dataset      beach    case lab_field  ...   beta       d50  roughness     r2
                0  ATKINSON2017  AUSTINMER  AU24-1         F  ...  0.102  0.000445   0.001112  1.979
                1  ATKINSON2017  AUSTINMER  AU24-2         F  ...  0.101  0.000445   0.001112  1.862
                2  ATKINSON2017  AUSTINMER  AU24-3         F  ...  0.115  0.000445   0.001112  1.695
                3  ATKINSON2017  AUSTINMER  AU24-4         F  ...  0.115  0.000445   0.001112  1.604
                4  ATKINSON2017  AUSTINMER  AU24-5         F  ...  0.115  0.000445   0.001112  1.515
                [5 rows x 10 columns]
            >>> df.columns
            Index(['dataset', 'beach', 'case', 'lab_field', 'hs', 'tp', 'beta', 'd50',
                   'roughness', 'r2'],dtype='object')
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
