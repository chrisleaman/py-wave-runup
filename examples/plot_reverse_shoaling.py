"""
Reverse shoaling
=====================================


This script demonstrates an example that requires reverse-shoaling before
run-up is calculated.

First, let's import our required packages:
"""

#############################################


import numpy as np
import pandas as pd

from py_wave_runup import utils

#############################################
# First, create a dummy data set. Water depth of observed/measured/modeled significant
# wave height. Depth is positive, in meters. Depths between 90 and 100 m should yield a
# mix of deep and intermediate water waves for the following Hs, Tp wave parameter
# ranges.

df = pd.DataFrame(columns=["water_depth", "Tp", "Hs"])
df["water_depth"] = np.random.uniform(90.0, 100.0, 5)
# Wave period in seconds
df["Tp"] = np.random.uniform(8, 14, 5)
# Significant wave height
df["Hs"] = np.random.uniform(3, 8, 5)
# Beach slope
df["beta"] = np.random.uniform(0.05, 0.2)


#############################################
# Reverse shoaling of wave forecasts:

# Calculate the deep water wave length
df = df.copy()  # Ensure we work with a copy to avoid pandas warnings
df.loc[:, "Lo"] = utils.calculate_Lo(df)
# Evaluate whether in shallow, intermediate, or deep water
df.loc[:, "wave_depth"] = utils.determine_waveDepth(df)
# Compute the deep water wave height
df.loc[:, "Ho"] = utils.reverse_shoal(df)

df
