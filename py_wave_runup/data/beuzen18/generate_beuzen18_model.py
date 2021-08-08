"""
File to manually generate new Beuzen18 model. A new model file needs to be generated
each time sklearn gets updated to a new version.

Code and data copied from:
https://github.com/TomasBeuzen/BeuzenEtAl_2019_NHESS_GP_runup_model/blob/master/paper_code/Beuzen_et_al_2019_code.ipynb
"""

import pandas as pd
from joblib import dump, load
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


def train_model(save_model=False):
    data_file = "./py_wave_runup/data/beuzen18/lidar_runup_data_for_GP_training.csv"
    df = pd.read_csv(data_file, index_col=0)

    # Define features and response data
    X = df.drop(
        columns=df.columns[-1]
    )  # Drop the last column to retain input features (Hs, Tp, slope)
    y = df[[df.columns[-1]]]  # The last column is the predictand (R2)

    # Specify the kernel to use in the GP
    kernel = RBF(0.1, (1e-2, 1e2)) + WhiteKernel(1, (1e-2, 1e2))

    # Train GP model on training dataset
    gp = GaussianProcessRegressor(
        kernel=kernel, n_restarts_optimizer=9, normalize_y=True, random_state=123
    )
    gp.fit(X, y)

    if save_model:
        dump(gp, "gp_runup_model.joblib")


if __name__ == "__main__":
    train_model()
