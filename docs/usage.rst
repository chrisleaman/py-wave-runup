
Usage
-----

.. code:: python

    from py_wave_runup import models

    model_sto06 = models.Stockdon2006(Hs=4, Tp=12, beta=0.1)

    model_sto06.R2     # 2.54
    model_sto06.setup  # 0.96
    model_sto06.sinc   # 2.06
    model_sto06.sig    # 1.65
