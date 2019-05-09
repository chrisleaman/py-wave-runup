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
    def setup(self):
        raise NotImplementedError

    @property
    def sinc(self):
        raise NotImplementedError

    @property
    def sig(self):
        raise NotImplementedError

    @property
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


class Power2018(RunupModel):
    """
    This class implements the empirical wave runup model from:

        Power, H.E., Gharabaghi, B., Bonakdari, H., Robertson, B., Atkinson, A.L.,
        Baldock, T.E., 2018. Prediction of wave runup on beaches using
        Gene-Expression Programming and empirical relationships. Coastal Engineering.
        https://doi.org/10.1016/j.coastaleng.2018.10.006

    Examples:
        Calculate 2% exceedence runup level given Hs=4m, Tp=11s, beta=0.1.

        >>> from py_wave_runup.models import Power2018
        >>> pow18 = Power2018(Hs=1, Tp=8, beta=0.07, r=0.00075)
        >>> pow18.R2
        1.12
    """

    doi = "10.1016/j.coastaleng.2018.10.006"

    def __init__(self, Hs=None, Tp=None, beta=None, Lp=None, r=None):
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
            r (:obj:`float` or :obj:`list`): Hydraulic roughness length. Can be
                approximated by :math:`r=2.5D_{50}`.
        """

        RunupModel.__init__(self, Hs, Tp, beta, Lp)

        self.r = np.atleast_1d(r)

        # Ensure hydraulic roughness is specified
        if r is None:
            raise ValueError("Expected either hydraulic roughness, r, arg")

    @property
    def R2(self):
        """
        Returns:
            The 2% exceedence runup level, based on following dimensionless parameters:

            .. math::

                x_{1} &= \\frac{H_{s}}{L_{p}} \\\\
                x_{2} &= \\beta \\\\
                x_{3} &= \\frac{r}{H_{s}}

            The final equation is given by the form:

            .. math::

               R_{2} &= H_{s} \\times ( \\\\
                &(x_{2} + (((x_{3} \\times 3) / e^{-5}) \\times ((3 \\times x_{3}) \\times x_{3}))) \\\\
                &+ ((((x_{1} + x_{3}) - 2) - (x_{3} - x_{2})) + ((x_{2} - x_{1}) - x_{3})) \\\\
                &+ (((x_{3}^{x_{1}}) - (x_{3}^{\\frac{1}{3}})) - ((e^{x_{2}})^{(x_{1} \\times 3)})) \\\\
                &+ \\sqrt{(((x_{3} + x_{1}) - x_{2}) - (x_{2} + \\log_{10}x_{3}))} \\\\
                &+ ((((x_{2}^{2}) / (x_{1}^{\\frac{1}{3}}))^{(x_{1}^{\\frac{1}{3}})}) - \\sqrt{x_{3}}) \\\\
                &+ ( (x_{2} + ((x_{3} / x_{1})^{\\frac{1}{3}})) + (\\log(2) - (1 / (1 + e^{-(x_{2} + x_{3})}))) ) \\\\
                &+ ((\\sqrt{x_{3}} - (((3^{2}) + 3) \\times (x_{2}^{2})))^{2}) \\\\
                &+ ((((x_{3} \\times -5)^{2})^{2}) + (((x_{3} + x_{3}) \\times x_{1}) / (x_{2}^{2}))) \\\\
                &+ \\log{(\\sqrt{((x_{2}^{2}) + (x_{3}^{\\frac{1}{3}}))} + ((x_{2} + 3)^{\\frac{1}{3}}))} \\\\
                &+ ( (((x_{1} / x_{3}) \\times (-5^{2})) \\times (x_{3}^{2})) - \\log_{10}{(1 / (1 + \\exp^{-(x_{2} + x_{3})}))} ) \\\\
                &+ (x_{1}^{x_{3}}) \\\\
                &+ \\exp^{-((((x_{3} / x_{1})^{\\exp^{4}}) + ((\\exp^{x_{3}})^{3}))^{2})} \\\\
                &+ \\exp^{(\\log{(x_{2} - x_{3})} - \\log{\\exp^{-((-1 + x_{1})^{2})}})} \\\\
                &+ ((\\sqrt{4} \\times (((x_{3} / x_{2}) - x_{2}) - (0 - x_{1})))^{2}) \\\\
                &+ (2 \\times ((((-5 \\times x_{3}) + x_{1}) \\times (2 - x_{3})) - 2)) \\\\
                &+ ((\\sqrt{4} \\times (((x_{3} / x_{2}) - x_{2}) - (0 - x_{1})))^{2}) \\\\
                &+ ((((-5 + x_{1}) - x_{2}) \\times (x_{2} - x_{3})) \\times ((x_{1} - x_{2}) - (-4^{-5}))) \\\\
                &+ (\\exp^{-((x_{2} + (-5 - x_{1}))^{2})} + ((x_{2} + 5) \\times (x_{3}^{2}))) \\\\
                &+ \\sqrt{ 1 / ( 1 + \\exp^{ -( (\\exp^{x_{1}} - \\exp^{-((x_{3} + x_{3})^{2})}) + ((x_{1}^{x_{3}}) - (x_{3} \\times 4)) ) } ) } \\\\
                &+ ( ( \\exp^{ -( ( ( ( \\exp^{ -( ( (\\sqrt{x_{3}} \\times 4) + (1 / (1 + \\exp^{-(x_{2} + 2)})) )^{2} ) } )^{2} ) + x_{1} )^{2} ) } )^{3} ) \\\\
                )
        """

        # Power et al. defines these three dimensionless parameters in Eqn (9)
        x1 = self.Hs / self.Lp
        x2 = self.beta
        x3 = self.r / self.Hs

        result = self.Hs * (
            (x2 + (((x3 * 3) / np.exp(-5)) * ((3 * x3) * x3)))
            + ((((x1 + x3) - 2) - (x3 - x2)) + ((x2 - x1) - x3))
            + (((x3 ** x1) - (x3 ** (1 / 3))) - (np.exp(x2) ** (x1 * 3)))
            + np.sqrt((((x3 + x1) - x2) - (x2 + np.log10(x3))))
            + ((((x2 ** 2) / (x1 ** (1 / 3))) ** (x1 ** (1 / 3))) - np.sqrt(x3))
            + (
                (x2 + ((x3 / x1) ** (1 / 3)))
                + (np.log(2) - (1 / (1 + np.exp(-(x2 + x3)))))
            )
            + ((np.sqrt(x3) - (((3 ** 2) + 3) * (x2 ** 2))) ** 2)
            + ((((x3 * -5) ** 2) ** 2) + (((x3 + x3) * x1) / (x2 ** 2)))
            + np.log((np.sqrt(((x2 ** 2) + (x3 ** (1 / 3)))) + ((x2 + 3) ** (1 / 3))))
            + (
                (((x1 / x3) * (-5 ** 2)) * (x3 ** 2))
                - np.log10((1 / (1 + np.exp(-(x2 + x3)))))
            )
            + (x1 ** x3)
            + np.exp(-((((x3 / x1) ** np.exp(4)) + (np.exp(x3) ** 3)) ** 2))
            + np.exp((np.log((x2 - x3)) - np.log(np.exp(-((-1 + x1) ** 2)))))
            + ((np.sqrt(4) * (((x3 / x2) - x2) - (0 - x1))) ** 2)
            + (2 * ((((-5 * x3) + x1) * (2 - x3)) - 2))
            + ((np.sqrt(4) * (((x3 / x2) - x2) - (0 - x1))) ** 2)
            + ((((-5 + x1) - x2) * (x2 - x3)) * ((x1 - x2) - (-4 ** -5)))
            + (np.exp(-((x2 + (-5 - x1)) ** 2)) + ((x2 + 5) * (x3 ** 2)))
            + np.sqrt(
                1
                / (
                    1
                    + np.exp(
                        -(
                            (np.exp(x1) - np.exp(-((x3 + x3) ** 2)))
                            + ((x1 ** x3) - (x3 * 4))
                        )
                    )
                )
            )
            + (
                (
                    np.exp(
                        -(
                            (
                                (
                                    (
                                        np.exp(
                                            -(
                                                (
                                                    (np.sqrt(x3) * 4)
                                                    + (1 / (1 + np.exp(-(x2 + 2))))
                                                )
                                                ** 2
                                            )
                                        )
                                    )
                                    ** 2
                                )
                                + x1
                            )
                            ** 2
                        )
                    )
                )
                ** 3
            )
        )

        result = self._return_one_or_array(result)
        return result


class Holman1986(RunupModel):
    """
    This class implements the empirical wave runup model from:

        Holman, R.A., 1986. Extreme value statistics for wave run-up on a natural
        beach. Coastal Engineering 9, 527–544. https://doi.org/10.1016/0378-3839(
        86)90002-5

    Examples:
        Calculate 2% exceedence runup level, including setup component given Hs=4m,
        Tp=11s, beta=0.1.

        >>> from py_wave_runup.models import Power2018
        >>> hol86 = Holman1986(Hs=4, Tp=11, beta=0.1)
        >>> hol86.R2
        3.09
        >>> hol86.setup
        0.8
    """

    doi = "10.1016/0378-3839(86)90002-5"

    @property
    def R2(self):
        """
        Returns:
            The 2% exceedence runup level, given by

                .. math:: R_{2} = 0.83 \\tan{\\beta} \\sqrt{H_{s}+L_{p}} + 0.2 H_{s}
        """
        result = 0.83 * np.tan(self.beta) * np.sqrt(self.Hs * self.Lp) + 0.2 * self.Hs
        result = self._return_one_or_array(result)
        return result

    @property
    def setup(self):
        """
        Returns:
            The setup level using:

                .. math:: S = 0.2 H_{s}
        """
        result = 0.2 * self.Hs
        result = self._return_one_or_array(result)
        return result


class Nielsen2009(RunupModel):
    """
    This class implements the empirical wave runup model from:

        P. Nielsen, Coastal and Estuarine Processes, Singapore, World Scientiﬁc, 2009.

    Examples:
        Calculate 2% exceedence runup level given Hs=4m, Tp=11s, beta=0.1.

        >>> from py_wave_runup.models import Nielsen2009
        >>> niel = Holman1986(Hs=4, Tp=11, beta=0.1)
        >>> niel.R2
        3.27
    """

    @property
    def R2(self):
        """
        Returns:
            The 2% exceedence runup level, given by

                .. math:: R_{2} = 1.98L_{R} + Z_{100}

            This relationship was first suggested by Nielsen and Hanslow (1991). The
            definitions for :math:`L_{R}` were then updated by Nielsen (2009),
            where :math:`L_{R} = 0.6 \\tan{\\beta} \\sqrt{H_{rms}L_{s}}` for
            :math:`\\tan{\\beta} \geq 0.1` and :math:`L_{R} = 0.06\\sqrt{H_{rms}L_{s}}`
            for :math:`\\tan{\\beta}<0.1`. Note that :math:`Z_{100}` is the highest
            vertical level passed by all swash events in a time period and is usually
            taken as the tide varying water level.
        """

        # Two different definitions of LR dependant on slope:
        beta_mask = np.tan(self.beta) < 0.1
        LR = 0.6 * np.tan(self.beta) * np.sqrt(self.Hs * self.Lp)
        LR[beta_mask] = 0.06 * np.sqrt(self.Hs * self.Lp)

        result = 1.98 * LR
        result = self._return_one_or_array(result)
        return result
