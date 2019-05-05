Usage
-----

First, make sure that the package is :doc:`installed <installation>`.

Now, we import the ``models`` module from ``py_wave_runup``. This is where all our
empirical wave runup models are stored.

.. code:: python

    from py_wave_runup import models

Then, we can pick a model from the :doc:`list of available wave runup models
<models>` to use. Here we defined the wave height, wave period and slope used to
calculate runup using the Stockdon et al. (2006) model.

.. code:: python

    model_sto06 = models.Stockdon2006(Hs=4, Tp=12, beta=0.1)

Our model now gives us access to our wave runup parameter which have been calculated
using the model.

.. code:: python

    model_sto06.R2     # 2.54
    model_sto06.setup  # 0.96
    model_sto06.sinc   # 2.06
    model_sto06.sig    # 1.65
