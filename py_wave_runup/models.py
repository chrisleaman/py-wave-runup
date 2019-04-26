from abc import ABCMeta, abstractmethod

import numpy as np


class RunupModel(metaclass=ABCMeta):
    """
    Abstract base class which our empirical runup models will inherit from
    """

    doi = None

    def __init__(self, Hs=None, Tp=None, beta=None, Lp=None):
        """
        Args:
            Hs (:obj:`float` or :obj:`list`): Significant wave height. In order to
                account for energy dissipation in the nearshore, transform the wave to
                the nearshore, then reverse-shoal to deep water.
            beta (:obj:`float` or :obj:`list`): Beach slope. Typically defined as the
                slope between the region of :math:`\\pm2\\sigma` where :math:`\\sigma`
                is the standard deviation of the continuous water level record.
            Tp (:obj:`float` or :obj:`list`): Peak wave period.
                Must be defined if :attr:`Lp` is not defined.
            Lp (:obj:`float` or :obj:`list`): Peak wave length
                Must be definied if :attr:`Tp` is not defined.
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
    """

    This class implements the empirical wave runup model from:

        Stockdon, H. F., Holman, R. A., Howd, P. A., & Sallenger, A. H. (2006).
        Empirical  parameterization of setup, swash, and runup. Coastal Engineering,
        53(7), 573–588. https://doi.org/10.1016/j.coastaleng.2005.12.005

    Examples:
        Calculate 2% exceedence runup level, including setup component and swash
        component given Hs=4m, Tp=11s, beta=0.1.

        >>> from py_wave_runup.models import Stockdon2006
        >>> sto06 = Stockdon2006(Hs=4, Tp=11, beta=0.1)
        >>> sto06.R2
        2.54
        >>> sto06.setup
        0.96
        >>> sto06.swash
        2.64
    """

    doi = "10.1016/j.coastaleng.2005.12.005"

    @property
    def R2(self):
        """
        Returns:
            The 2% exceedence runup level. For dissipative beaches (i.e.
            :math:`\\zeta < 0.3`) Eqn (18) from the paper is used:

            .. math:: R_{2} = 0.043(H_{s}L_{p})^{0.5}

            For intermediate and reflective beaches (i.e. :math:`\\zeta > 0.3`),
            the function returns the result from Eqn (19):

            .. math::

                R_{2} = 1.1 \\left( 0.35 \\beta (H_{s}L_{p})^{0.5} + \\frac{H_{s}L_{p}(
                0.563 \\beta^{2} +0.004)^{0.5}}{2} \\right)
        """

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
        """
        Returns:
            The setup level using Eqn (10):

                .. math:: \\bar{\\eta} = 0.35 \\beta (H_{s}L_{p})^{0.5}


        """
        result = 0.35 * self.beta * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def sinc(self):
        """
        Returns:
            Incident component of swash using Eqn (11):

                .. math:: S_{inc} = 0.75 \\beta (H_{s}L_{p})^{0.5}
        """
        result = 0.75 * self.beta * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def sig(self):
        """
        Returns:
            Infragravity component of swash using Eqn (12):

                .. math:: S_{ig} = 0.06 (H_{s}L_{p})^{0.5}
        """
        result = 0.06 * (self.Hs * self.Lp) ** 0.5
        result = self._return_one_or_array(result)
        return result

    @property
    def swash(self):
        """
        Returns:
            Total amount of swash using Eqn (7):

                .. math:: S = \\sqrt{S_{inc}^{2}+S_{ig}^{2}}
        """
        result = np.sqrt(self.sinc ** 2 + self.sig ** 2)
        result = self._return_one_or_array(result)
        return result
