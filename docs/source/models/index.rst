======
Models
======

DelftDashboard supports several numerical models for coastal, estuarine, and
riverine simulations. Each model is exposed through a dedicated tab panel in the
GUI, where users can configure the domain, physics, boundary conditions, output,
and other settings before running the simulation.

The following models are available:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Model
     - Description
   * - :doc:`sfincs_hmt`
     - SFINCS (HydroMT) -- fast compound flooding model for coastal, fluvial, and pluvial flooding.
   * - :doc:`hurrywave_hmt`
     - HurryWave (HydroMT) -- third-generation spectral wave model for nearshore and coastal wave transformation.
   * - :doc:`delft3dfm`
     - Delft3D-FM -- full 2D/3D hydrodynamic model with flexible mesh for tidal, storm surge, and river flow simulations.

.. toctree::
   :maxdepth: 2
   :caption: Available Models

   sfincs_hmt
   hurrywave_hmt
   delft3dfm
