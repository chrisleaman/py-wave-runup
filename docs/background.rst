
Background
----------

Wave runup refers to the final part of a wave's journey as it travels from offshore
onto the beach. It is observable by anyone who goes to the beach and watches the edge
of the water "runup" and rundown the beach. It is comprised of two components:

    - **setup**: the height of the time averaged superelevation of the mean water level
      above the Still Water Level (SWL)
    - **swash**: the height of the time varying fluctuation of the instantaneous water
      level about the setup elevation

Setup, swash and other components of Total Water Level (TWL) rise are shown in this
handy figure below.

.. image:: ./_static/VitousekDoubling2017Fig1.jpg
..

    | Figure from Vitousek et al. (2017) [#vit17]_

Wave runup can contribute a significant portion of the increase in TWL in coastal
storms causing erosion and inundation. For example, Stockdon et al. (2006) [#sto06]_
collated data from numerous experiments, some of which showed wave runup 2% excedence
heights in excess of 3 m during some storms.

Given the impact such a large increase in TWL can have on coastlines, there has been
much research conducted to try improve our understanding of wave runup processes.
Although there are many processes which can influence wave runup (such as nonlinear
wave transformation, wave reflection, three-dimensional effects, porosity, roughness,
permeability and groundwater) [#cem06]_, many attempts have been made to derive
empirical relationships based on easily measurable parameters. Typically, empirical
wave runup models include:

    - **Hs**: significant wave height
    - **Tp**: peak wave length
    - **beta**: beach slope

This python package attempts to consolidate the work done by others in this field and
collate the numerous empirical relationships for wave runup which have been published.

--------

.. [#vit17] Vitousek, Sean, Patrick L. Barnard, Charles H. Fletcher, Neil Frazer,
       Li Erikson, and Curt D. Storlazzi. "Doubling of Coastal Flooding Frequency
       within Decades Due to Sea-Level Rise." Scientific Reports 7, no. 1 (May 18,
       2017): 1399. https://doi.org/10.1038/s41598-017-01362-7.
.. [#sto06] Stockdon, Hilary F., Robert A. Holman, Peter A. Howd, and Asbury H. Sallenger.
       "Empirical Parameterization of Setup, Swash, and Runup." Coastal Engineering 53,
       no. 7 (May 1, 2006): 573-88. https://doi.org/10.1016/j.coastaleng.2005.12.005
.. [#cem06] United States, Army, and Corps of Engineers. Coastal Engineering Manual.
       Washington, D.C.: U.S. Army Corps of Engineers, 2006.
