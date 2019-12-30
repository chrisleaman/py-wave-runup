import math
import random


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
