"""
This module implements different ensemble methods of predicting wave runup. It uses
the models provided by models.py
"""

from py_wave_runup import models
import pandas as pd


class EnsembleRaw:
    """
    This class returns the values for all runup models defined in models.py seperately,
    i.e. no combining is performed.
    """

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
                Must be defined if ``Lp`` is not defined.
            Lp (:obj:`float` or :obj:`list`): Peak wave length
                Must be definied if ``Tp`` is not defined.
            r (:obj:`float` or :obj:`list`): Hydraulic roughness length. Can be
                approximated by :math:`r=2.5D_{50}`.
        """

        self.Hs = Hs
        self.Tp = Tp
        self.beta = beta
        self.Lp = Lp
        self.r = r

        # Get list of all runup models
        self.runup_models = models.RunupModel.__subclasses__()

    def estimate(self, param):
        """
        Returns:
            Returns a pandas dataframe where each column contains the estimates
            returned by each runup model

        Args:
            param (:obj:`str`): `R2`, `setup`, `sig`, `sinc` or `swash`

        Examples:
        Get a dataframe containing all wave runup model predictions for Hs=4,
        Tp=11 and beta=0.1.

        >>> from py_wave_runup.ensembles import EnsembleRaw
        >>> ensemble = EnsembleRaw(Hs=4, Tp=11, beta=0.1)
        >>> ensemble_r2 = ensemble.estimate('R2')
        >>> ensemble_r2
           Stockdon2006_R2  Power2018_R2  ...  Atkinson2017_R2  Senechal2011_R2
        0         2.542036           NaN  ...           3.1775         1.972371
        <BLANKLINE>
        [1 rows x 8 columns]
        """
        return self._model_estimates(param)

    def _model_estimates(self, param):
        """
        Returns:
            Returns a pandas dataframe where each column contains the estimates
            returned by each runup model

        Args:
            param (:obj:`str`): `R2`, `setup`, `sig`, `sinc` or `swash`
        """

        valid_params = ["R2", "setup", "sig", "sinc", "swash"]
        if param not in valid_params:
            raise ValueError(f'param must be one of {" or ".format(valid_params)}')

        # Store results in dictionary
        results = {}

        for model in self.runup_models:

            # Check that model has the attribute we need (some models don't estimate
            # infragravity/incident swash)
            if hasattr(model, param):
                model_name = model.__name__
                results[f"{model_name}_{param}"] = getattr(
                    model(Hs=self.Hs, Tp=self.Tp, beta=self.beta, r=self.r), param
                )

        # Due to the way pandas constructs dataframes, we must specify the results in
        # a list if we only have one set of conditions to return.
        if hasattr(type(self.Hs), "__iter__"):
            df = pd.DataFrame.from_dict(results)
        else:
            df = pd.DataFrame.from_dict([results])
        return df


class EnsembleMean(EnsembleRaw):
    def estimate(self, param):
        """
        Returns:
            Returns the mean parameter given by all the runup models.

        Args:
            param (:obj:`str`): `R2`, `setup`, `sig`, `sinc` or `swash`

        Examples:
        Get a pandas series containing the mean wave runup model predictions for Hs=4,
        Tp=11 and beta=0.1.

        >>> from py_wave_runup.ensembles import EnsembleMean
        >>> ensemble = EnsembleMean(Hs=[3,4], Tp=[10,11], beta=[0.09,0.1])
        >>> ensemble_r2 = ensemble.estimate('R2')
        >>> ensemble_r2
        0    2.01381
        1    2.64924
        Name: mean_R2, dtype: float64
        """
        df = self._model_estimates(param)
        return df.mean(axis=1).rename(f"mean_{param}")


if __name__ == "__main__":
    ensemble = EnsembleRaw(Hs=1, Tp=8, beta=0.05)
    # ensemble = EnsembleRaw(Hs=[1,2], Tp=[8,10], beta=[0.05,0.01])
    r2 = ensemble.estimate("R2")

    ensemble_mean = EnsembleMean(Hs=[1, 2], Tp=[8, 10], beta=[0.05, 0.01])
    mean_r2 = ensemble_mean.estimate("R2")

    print("Done")
