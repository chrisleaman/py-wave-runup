"""
Script by: Mandi Thran
Date: 05/08/2021

This script demonstrates an example that requires reverse-shoaling before
run-up is calculated.
"""

# =========== Modules ===========#
import pandas as pd
import numpy as np
from py_wave_runup import models
from py_wave_runup import utils


# =========== Create a dummy data set ===========#
df = pd.DataFrame(columns=["water_depth", "Tp", "Hs"])
# Water depth of observed/measured/modeled significant wave height
# Depth is positive, in meters
# Depths between 90 and 100 m should yield a mix of deep and intermediate water waves
# For the following Hs, Tp wave parameter ranges
df["water_depth"] = np.random.uniform(90.0, 100.0, 5)
# Wave period in seconds
df["Tp"] = np.random.uniform(8, 14, 5)
# Significant wave height
df["Hs"] = np.random.uniform(3, 8, 5)
# Beach slope
df["beta"] = np.random.uniform(0.05, 0.2)


# =========== Reverse Shoaling of Wave Forecasts ===========#
# Calculate the deep water wave length
df["Lo"] = utils.calculate_Lo(df)
# Evaluate whether in shallow, intermediate, or deep water
df["wave_depth"] = utils.determine_waveDepth(df)
# Compute the deep water wave height
df["Ho"] = utils.reverse_shoal(df)

print(df)
