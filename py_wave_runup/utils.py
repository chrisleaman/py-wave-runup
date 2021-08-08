import math
import random

import numpy as np
import pandas as pd


class PerlinNoise(object):
    """
    Perlin noise is used to generate random timeseries in the datasets module.

    Implementation of 1D Perlin Noise ported from C code:
    https://github.com/stegu/perlin-noise/blob/master/src/noise1234.c
    """

    def __init__(self, num_octaves, persistence, noise_scale=0.188):
        self.num_octaves = num_octaves

        self.noise_scale = 0.188

        self.octaves = [PerlinNoiseOctave() for i in range(self.num_octaves)]
        self.frequencies = [1.0 / pow(2, i) for i in range(self.num_octaves)]
        self.amplitudes = [
            pow(persistence, len(self.octaves) - i) for i in range(self.num_octaves)
        ]

    def noise(self, x):
        noise = [
            self.octaves[i].noise(
                xin=x * self.frequencies[i], noise_scale=self.noise_scale
            )
            * self.amplitudes[i]
            for i in range(self.num_octaves)
        ]

        return sum(noise)


class PerlinNoiseOctave(object):
    """
    Perlin noise is used to generate random timeseries in the datasets module.
    """

    def __init__(self, num_shuffles=100):
        self.p_supply = [i for i in range(0, 256)]

        for i in range(num_shuffles):
            random.shuffle(self.p_supply)

        self.perm = self.p_supply * 2

    def noise(self, xin, noise_scale):
        ix0 = int(math.floor(xin))
        fx0 = xin - ix0
        fx1 = fx0 - 1.0
        ix1 = (ix0 + 1) & 255
        ix0 = ix0 & 255

        s = self.fade(fx0)

        n0 = self.grad(self.perm[ix0], fx0)
        n1 = self.grad(self.perm[ix1], fx1)

        return noise_scale * self.lerp(s, n0, n1)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def fade(self, t):
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    def grad(self, hash, x):
        h = hash & 15
        grad = 1.0 + (h & 7)  # Gradient value from 1.0 - 8.0
        if h & 8:
            grad = -grad  # Add a random sign
        return grad * x


def calculate_Lo(df):
    """
    Calculates the deep water wave length

    Input:
    df: pandas dataframe with at least the following columns:
        - df.Tp: Wave period in seconds

    Output:
        - A pandas series containing the deep water wavelength Lo in meters

    Example of use:
    df['Lo'] = utils.calculate_Lo(df)
    See examples/plot_reverse_shoaling.py
    """
    g = 9.81  # in m/s2
    Lo = (g * df.Tp * df.Tp) / (2.0 * np.pi)
    return Lo


def reverse_shoal_intermediate(
    waterDepthSeries=None, LoSeries=None, TpSeries=None, HsSeries=None
):
    """
    Computes deep water wave height assuming an intermediate wave depth condition.

    Input: pandas dataframe with at least the following columns:
        - waterDepthSeries: Pandas series containing water depth where wave height was
          measured/computed (meters)
        - LoSeries: Pandas series containing deep water wave length (seconds)
        - TpSeries: Pandas series containing wave period (s)
        - HsSeries: Pandas series containing height at the time of measurement/computation
          in intermediate water (m)

    Output:
        - Pandas series of reverse-shoaled deep water significant wave heights (m)

    Example of use:
    HoSeries = reverse_shoal_intermediate(waterDepthSeries=df.water_depth,
                                          LoSeries=df.Lo,
                                          TpSeries=df.Tp,
                                          HsSeries=df.Hs)
    """

    # Double-check that these are in fact intermediate water waves
    if (waterDepthSeries > (1.0 / 2.0) * LoSeries).any() == True:
        errorMessage = str(
            "ERROR: Deep water waves detected. "
            + "Water depth should be less than "
            + "1/2 * deep water wave length (Lo) "
            + "to satisfy intermediate wave condition. "
            + "For deep water waves, Hs = Ho"
        )
        print(errorMessage)
        raise ValueError("Deep water waves detected")
    if (waterDepthSeries < (1.0 / 50.0) * LoSeries).any() == True:
        errorMessage = str(
            "ERROR: Shallow water waves detected. "
            + "Water depth should be greater than "
            + "1/50 * deep water wave length (Lo) "
            + "to satisfy intermediate wave condition. "
        )
        print(errorMessage)

    # Main calculation
    g = 9.81  # in m/s2
    y = 4.03 * waterDepthSeries / (TpSeries ** 2)
    kd2 = y ** 2 + y / (
        1
        + (0.666 * y)
        + (0.355 * y ** 2)
        + (0.161 * y ** 3)
        + (0.0632 * y ** 4)
        + (0.0218 * y ** 5)
        + (0.00564 * y ** 6)
    )
    kh = np.sqrt(kd2)
    Cg = (
        g
        * TpSeries
        / (2 * np.pi)
        * (np.tanh(kh))
        * (0.5 * (1 + 2 * kh / np.sinh(2 * kh)))
    )
    Cgo = 1 / 4 * g * TpSeries / np.pi
    Ks = np.sqrt(Cgo / Cg)
    Hs0 = HsSeries / Ks
    return Hs0


def determine_waveDepth(df):
    """
    Determines whether a wave is in deep, intermediate, or shallow water

    Input:
    df: pandas dataframe containing at least the following columns:
        - df.water_depth: water depth where significant wave height was measured
          or computed (in meters, depth is positive)
        - df.Lo: deep water wave length in meters

    Output:
        - A pandas series containing the wave depth classification

    Example of use:
    df['wave_depth'] = utils.determine_waveDepth(df)
    See examples/plot_reverse_shoaling.py

    """
    # create a list of conditions
    conditions = [
        # Shallow water
        (df.water_depth < (1.0 / 50.0) * df.Lo),
        # Intermediate water
        (df.water_depth >= (1.0 / 50.0) * df.Lo)
        & (df.water_depth <= (1.0 / 2.0) * df.Lo),
        # Deep water
        (df.water_depth > (1.0 / 2.0) * df.Lo),
    ]

    # create a list of the values to assign for each condition
    values = ["shallow", "intermediate", "deep"]

    # create a new column and use np.select to assign values to it using our lists as arguments
    df["wave_depth"] = np.select(conditions, values)

    return df.wave_depth


def reverse_shoal(df_wave=None):
    """
    Calculates the deep water wave height given an inshore wave height at a
    particular depth

    For theory, additional code, and useful tools, refer to:
         https://github.com/csherwood-usgs/jsed/blob/master/Runup%20and%20Reverse%20Shoaling%2C%20USGS.html
    And: https://csherwood-usgs.github.io/jsed/Runup%20and%20Reverse%20Shoaling,%20USGS.html

    Args:
        df_wave: Input dataframe with column for water_depth, Tp, Hs, and wave_depth
            - "wave_depth" column: Indicates whether wave is in deep, intermediate, or shallow water.
              To generate a "wave_depth" column, see the function determine_waveDepth in utils.py

    Returns:
        Pandas series of reverse shoalled wave heights

    Note: only deals with intermediate and deep water wave conditions. Will return NaN if the wave meets a shallow water condition.

    Uses an approximation to solve dispersion eq.

    """

    df = df_wave.copy()

    # New column
    df["Ho"] = np.nan

    # Evaluate in deep water
    # Find rows that are labeled as having deep water waves
    # Set deep water wave height to Hs (since it's already in deep water)
    df.loc[df["wave_depth"] == "deep", "Ho"] = df.Hs

    # Evaluate in intermediate water
    # Make a new dataframe with only intermediate water waves by masking original dataframe
    # To avoid copy warning in pandas
    mask_int = df.wave_depth == "intermediate"
    df_int = df[mask_int]
    HoSeries = reverse_shoal_intermediate(
        waterDepthSeries=df_int.water_depth,
        LoSeries=df_int.Lo,
        TpSeries=df_int.Tp,
        HsSeries=df_int.Hs,
    )

    # Assign values in series to original dataframe
    df.loc[df["wave_depth"] == "intermediate", "Ho"] = HoSeries

    # Return series of values that matches the number
    # of rows in the original dataframe
    return df["Ho"].values
