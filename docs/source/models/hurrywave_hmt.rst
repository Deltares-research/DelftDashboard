====================
HurryWave (HydroMT)
====================

Overview
========

HurryWave is a third-generation spectral wave model designed for efficient
simulation of nearshore and coastal wave transformation. It solves the spectral
action balance equation on a regular grid and includes wind generation,
refraction, shoaling, wave breaking, and bottom friction. HurryWave is
well-suited for operational forecasting and large-scale wave hindcast studies
due to its computational efficiency.

In DelftDashboard the HurryWave model is set up through the HydroMT framework,
which handles grid generation, bathymetry interpolation, and other
pre-processing steps via the Model Maker toolbox.

Domain
======

The Domain tab displays the spatial extent and resolution of the HurryWave
grid. These values are read-only; the grid is created through the Model Maker
toolbox.

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Parameter
     - Description
     - Variable
   * - X0
     - X-coordinate of the grid origin
     - ``x0``
   * - Y0
     - Y-coordinate of the grid origin
     - ``y0``
   * - MMax
     - Number of grid cells in the x-direction
     - ``mmax``
   * - NMax
     - Number of grid cells in the y-direction
     - ``nmax``
   * - dX
     - Grid cell size in the x-direction
     - ``dx``
   * - dY
     - Grid cell size in the y-direction
     - ``dy``
   * - Rotation
     - Grid rotation angle in degrees
     - ``rotation``

Time Frame
==========

The Time Frame tab defines the temporal extent of the simulation.

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Parameter
     - Description
     - Variable
   * - Reference Time
     - Reference date and time for the simulation (epoch)
     - ``tref``
   * - Start Time
     - Simulation start date and time
     - ``tstart``
   * - Stop Time
     - Simulation stop date and time
     - ``tstop``
   * - Spin-up Time (s)
     - Duration of the spin-up period in seconds
     - ``tspinup``

Physics
=======

The Physics tab is divided into sub-panels for physical process parameters.

Constants
---------

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Air Density (kg/m3)
     - Density of air used in wind drag calculations
     - ``rhoa``
   * - Water Density (kg/m3)
     - Density of water used in wave computations
     - ``rhow``

Roughness
---------

The Roughness sub-panel is currently marked as under development (TBD). Future
releases will add bottom friction parameters for wave dissipation.

Meteo
-----

The Physics > Meteo sub-panel configures the wind drag formulation used in wave
generation.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Wind Drag
     - Wind drag coefficient formulation: Zijlema (2012) or Wu (1982)
     - ``winddrag``
   * - Cd Cap
     - Maximum wind drag coefficient (Wu formulation only)
     - ``cdcap``

Numerics
========

The Numerics tab is divided into two panels.

Spectral Domain
---------------

Defines the discrete spectral space used by the wave model.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Freq Min (Hz)
     - Lowest frequency in the spectral domain
     - ``freqmin``
   * - Freq Max (Hz)
     - Highest frequency in the spectral domain
     - ``freqmax``
   * - Frequency Bins
     - Number of frequency bins (logarithmically spaced)
     - ``nsigma``
   * - Directional Bins
     - Number of directional bins (equally spaced over 360 degrees)
     - ``ntheta``

Limiters
--------

Limiters control the maximum change in wave energy between grid cells to ensure
numerical stability.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Dmx1 (-)
     - First limiter parameter controlling maximum spectral change
     - ``dmx1``
   * - Dmx2 (-)
     - Second limiter parameter controlling maximum spectral change
     - ``dmx2``

Boundary Conditions
===================

The Boundary Conditions tab manages wave boundary points along the open edges
of the grid.

Point Management
----------------

Boundary points can be added interactively on the map, deleted, or
auto-generated at a specified spacing along the mesh edges.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Action / Parameter
     - Description
     - Variable
   * - Add Point
     - Click on the map to place a new boundary point
     - 
   * - Delete Point
     - Remove the selected boundary point
     - 
   * - Create Points
     - Generate equally-spaced boundary points along the mesh
     - 
   * - Distance (m)
     - Spacing between auto-generated boundary points
     - ``boundary_dx``

Time Series vs 2D Spectra
-------------------------

Boundary forcing can be specified in two modes:

**Time Series** -- Parametric wave conditions specified per boundary point.
Each point receives constant-in-time values that can be edited individually or
applied to all points at once.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Hm0 (m)
     - Significant wave height
     - ``boundary_hm0``
   * - Tp (s)
     - Peak wave period
     - ``boundary_tp``
   * - Direction (deg)
     - Wave direction in nautical degrees (coming from)
     - ``boundary_wd``
   * - Directional Spreading (deg)
     - Directional spreading of the wave spectrum
     - ``boundary_ds``

The *Apply to All* button copies the current point values to every boundary
point.

**2D Spectra** -- Full two-dimensional energy density spectra read from file,
providing frequency- and direction-resolved boundary conditions. This mode is
used for nesting HurryWave inside a coarser wave model.

Meteo
=====

The Meteo tab defines the wind forcing applied to drive wave generation.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - File Type
     - Type of wind input: Uniform, Spider web, Regular Grid, or Regular Grid + Spider web
     - ``wind_type``
   * - Wind File (``.wnd``)
     - Uniform wind time series file (Uniform type)
     - ``wndfile``
   * - Spiderweb File (``.spw``)
     - Cyclone wind fields (Spider web types)
     - ``spwfile``
   * - AMU File (``.amu``)
     - Gridded u-component of wind (Regular Grid types)
     - ``amufile``
   * - AMV File (``.amv``)
     - Gridded v-component of wind (Regular Grid types)
     - ``amvfile``

Observation Points
==================

The Observation Points tab has two sub-tabs.

Regular
-------

Regular observation points are individual locations where bulk wave parameters
(Hm0, Tp, direction, etc.) are recorded at each output time step. Points can
be placed on the map, loaded from file, or saved.

Spectra
-------

Spectral observation points are locations where full 2D wave energy density
spectra are stored at the spectra output interval. These are useful for
nesting, validation against buoy data, or detailed spectral analysis.

Output
======

The Output tab controls what is written to disk and at what frequency.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Map output interval (s)
     - Interval for writing spatial map output
     - ``dtmapout``
   * - Max output interval (s)
     - Interval for writing maximum value maps
     - ``dtmaxout``
   * - His output interval (s)
     - Interval for writing time series at observation points
     - ``dthisout``
   * - Spectra output interval (s)
     - Interval for writing 2D spectral output at spectral observation points
     - ``dtsp2out``
   * - Restart output interval (s)
     - Interval for writing restart files
     - ``dtrstout``
