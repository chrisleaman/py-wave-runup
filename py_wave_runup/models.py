from abc import ABCMeta, abstractmethod

import numpy as np


class RunupModel(object):
    """
    Abstract base class which our empirical runup models will inherit from
    """

    __metaclass__ = ABCMeta

    doi = None

    def __init__(self, Hs=None, Tp=None, beta=None, Lp=None):
        """
        Test

        :param Hs: description
        :param Tp: description
        :param beta: description
        :param Lp: description
        """

        self.Hs = Hs
        self.Tp = Tp
        self.beta = beta
        self.Lp = Lp

        # Ensure wave length or peak period is specified
        if all(v is None for v in [Lp, Tp]):
            raise ValueError("Expected either Lp or Tp args")

        # Ensure input is atleast 1d numpy array, this is so we can handle lists,
        # arrays and floats.
        self.Hs = np.atleast_1d(Hs)
        self.beta = np.atleast_1d(beta)

        # Calculate wave length if it hasn't been specified.
        if not Lp:
            self.Tp = np.atleast_1d(Tp)
            self.Lp = 9.81 * (self.Tp ** 2) / 2 / np.pi
        else:
            self.Lp = np.atleast_1d(Lp)
            self.Tp = np.sqrt(2 * np.pi * self.Lp / 9.81)

        # Ensure arrays are of the same size
        if len(set(x.size for x in [self.Hs, self.Tp, self.beta, self.Lp])) != 1:
            raise ValueError("Input arrays are not the same length")

        # Calculate Iribarren number. Need since there are different
        # parameterizations for dissipative and intermediate/reflective beaches.
        self.zeta = self.beta / (self.Hs / self.Lp) ** (0.5)

    def _return_one_or_array(self, val):
        # If only calculating a single value, return a single value and not an array
        # with length one.
        if val.size == 1:
            return val.item()
        else:
            return val

    @property
    @abstractmethod
    def R2(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def setup(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def sinc(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def sig(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def swash(self):
        raise NotImplementedError


class Stockdon2006(RunupModel):

    doi = "10.1016/j.coastaleng.2005.12.005"

    @property
    def R2(self):
        # Generalized runup (Eqn 19)
        result = 1.1 * (
            0.35 * self.beta * (self.Hs * self.Lp) ** 0.5
            + ((self.Hs * self.Lp * (0.563 * self.beta ** 2 + 0.004)) ** 0.5) / 2
        )

        # For dissipative beaches (Eqn 18)
        dissipative_mask = self.zeta < 0.3
        result[dissipative_mask] = (
            0.043 * (self.Hs[dissipative_mask] * self.Lp[dissipative_mask]) ** 0.5
        )

        result = self._return_one_or_array(result)
        return result

    @property
    def setup(self):
        result = 0.35 * self.beta * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def sinc(self):
        result = 0.75 * self.beta * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def sig(self):
        result = 0.06 * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def swash(self):
        result = np.sqrt(self.sinc ** 2 + self.sig ** 2)
        result = self._return_one_or_array(result)
        return result
