==================
SFINCS (HydroMT)
==================

Overview
========

SFINCS (Super-Fast INundation of CoastS) is a reduced-complexity compound
flooding model designed for fast and accurate simulation of coastal, fluvial,
and pluvial flooding. It solves the shallow water equations on a regular or
sub-grid mesh and supports wind, barometric pressure, rainfall, river
discharges, and wave forcing. SFINCS is particularly suited for large-scale
flood hazard mapping, real-time forecasting, and ensemble simulations where
computational efficiency is critical.

In DelftDashboard the SFINCS model is set up through the HydroMT framework,
which handles grid generation, bathymetry interpolation, roughness assignment,
and other pre-processing steps via the Model Maker toolbox.

Domain
======

The Domain tab displays the spatial extent and resolution of the SFINCS grid.
These values are read-only in the model panel; the grid is created through the
Model Maker toolbox.

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
     - Number of grid cells in the M-direction
     - ``mmax``
   * - NMax
     - Number of grid cells in the N-direction
     - ``nmax``
   * - dX
     - Grid cell size in the X-direction
     - ``dx``
   * - dY
     - Grid cell size in the Y-direction
     - ``dy``
   * - Rotation
     - Grid rotation angle in degrees
     - ``rotation``
   * - Latitude
     - Latitude for Coriolis force (editable for projected CRS only)
     - ``latitude``

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

Physics
=======

The Physics tab is divided into five sub-panels covering physical process
settings.

Constants
---------

.. list-table::
   :header-rows: 1
   :widths: 20 60 20

   * - Parameter
     - Description
     - Variable
   * - Air Density (kg/m3)
     - Air density used in wind drag computation
     - ``rhoa``
   * - Water Density (kg/m3)
     - Water density
     - ``rhow``

Roughness
---------

For sub-grid models, roughness is embedded in the sub-grid tables and cannot be
edited directly on this panel. For regular-grid models, the following options
are available.

:Roughness Type: Controls how roughness is specified.

  - **Uniform** -- a single Manning coefficient applied everywhere.
  - **Land-sea interface** -- separate Manning values for land and sea cells,
    separated by an elevation threshold.
  - **File** -- Manning values read from an external ``.rgh`` file.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Manning
     - Uniform Manning roughness coefficient
     - ``manning``
   * - Manning (land)
     - Manning coefficient for land cells
     - ``manning_land``
   * - Manning (sea)
     - Manning coefficient for sea cells
     - ``manning_sea``
   * - Land level (m)
     - Elevation threshold separating land from sea
     - ``rgh_lev_land``
   * - Manning File
     - Path to external roughness file (``.rgh``)
     - ``manningfile``

Advection
---------

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Advection
     - Enable or disable the advection term (on/off)
     - ``advection``
   * - Advection Limiter
     - Limiter on the advection term (visible when advection is on)
     - ``advlim``

Viscosity
---------

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Viscosity
     - Enable or disable viscosity (on/off)
     - ``viscosity``
   * - Nuvisc
     - Viscosity scale factor; effective viscosity is computed as ``nuvisc * dx``
     - ``nuvisc``

Meteo
-----

The Physics > Meteo sub-panel configures wind drag, barometric pressure, and
infiltration parameters.

**Wind Drag**

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Number of breakpoints
     - Number of (wind speed, Cd) breakpoints (2 or 3)
     - ``cdnrb``
   * - Wind speed 1 / Cd 1
     - First breakpoint: wind speed (m/s) and drag coefficient
     - ``wind_speed_1``, ``cd_1``
   * - Wind speed 2 / Cd 2
     - Second breakpoint
     - ``wind_speed_2``, ``cd_2``
   * - Wind speed 3 / Cd 3
     - Third breakpoint (visible when 3 breakpoints selected)
     - ``wind_speed_3``, ``cd_3``

**Barometric Pressure**

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Include pressure
     - Include barometric pressure gradients in flux computation
     - ``baro``
   * - Pressure Correction (Pa)
     - Background pressure for inverse barometer correction at boundaries
     - ``pavbnd``
   * - Ambient Pressure (Pa)
     - Background air pressure
     - ``gapres``

**Infiltration**

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Infiltration Rate (mm/h)
     - Constant infiltration rate
     - ``qinf``

Numerics
========

The Numerics tab controls the numerical scheme settings.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Alpha (-)
     - Courant coefficient alpha for the time step limiter
     - ``alpha``
   * - Theta (-)
     - Smoothing coefficient theta
     - ``theta``
   * - Threshold Depth (m)
     - Minimum water depth for flow computation
     - ``huthresh``
   * - Stop Depth (m)
     - Simulation stops when this depth is exceeded anywhere
     - ``stopdepth``
   * - Spin-up Time (s)
     - Duration of spin-up period in seconds
     - ``tspinup``
   * - Wiggle Suppression
     - Enable wiggle suppression (sub-grid models only)
     - ``wiggle_suppression``

Boundary Conditions
===================

The Boundary Conditions tab manages water level boundary points placed along
the open boundaries of the grid.

Point Management
----------------

Boundary points can be added interactively on the map, deleted, or
auto-generated at a specified spacing along the mesh edges. Points can be loaded
from and saved to file.

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

Time Series vs Astronomical
---------------------------

Boundary conditions can be specified in two modes, selected via radio buttons:

**Time Series** -- Generate water level time series for all points based on a
chosen signal shape:

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Shape
     - Signal shape: Constant, Gaussian, Sinusoidal, or Astronomical tide
     - ``boundary_conditions_timeseries_shape``
   * - Time Step (s)
     - Time step for the output time series (bzs file)
     - ``boundary_conditions_timeseries_time_step``
   * - Offset (m)
     - Water level offset in metres
     - ``boundary_conditions_timeseries_offset``

*Sinusoidal shape additional parameters:*

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Amplitude (m)
     - Sinusoidal amplitude
     - ``boundary_conditions_timeseries_amplitude``
   * - Phase (deg)
     - Sinusoidal phase in degrees
     - ``boundary_conditions_timeseries_phase``
   * - Period (s)
     - Sinusoidal period in seconds
     - ``boundary_conditions_timeseries_period``

*Gaussian shape additional parameters:*

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Peak (m)
     - Gaussian peak value in metres
     - ``boundary_conditions_timeseries_peak``
   * - Peak Time (s)
     - Time of peak in seconds after the reference time
     - ``boundary_conditions_timeseries_tpeak``
   * - Duration (s)
     - Duration of the peak in seconds
     - ``boundary_conditions_timeseries_duration``

**Astronomical** -- Generate tidal boundary conditions from a global tide
model. Select a tide model from the drop-down and press *Generate From Tide
Model* to produce a ``.bca`` file with harmonic constituents for every boundary
point.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Tide Model
     - Global tide model used for constituent extraction
     - ``boundary_conditions_tide_model``

Discharges
==========

The Discharges tab manages point sources of water (river inflows, pump
stations, etc.). Discharge points are placed on the map and associated with
time-varying flow rates.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Action
     - Description
   * - Add Point
     - Click on the map to place a discharge point
   * - Delete Point
     - Remove the selected discharge point
   * - Load
     - Load discharge points from file
   * - Save
     - Save discharge points to file

Structures
==========

The Structures tab contains three sub-tabs for hydraulic structures.

Thin Dams
---------

Thin dams are infinitely thin barriers that block flow between adjacent cells.
They are defined as polylines drawn on the map. Typical uses include levees,
dikes, and road embankments that are narrower than a grid cell.

Weirs
-----

Weirs are flow-controlling structures with a defined crest level. Water can
flow over the weir when the upstream level exceeds the crest. The Weirs sub-tab
is only available when weir support is enabled.

Drainage
--------

Drainage structures allow water to be removed from the model domain at
specified rates, representing storm drains, culverts, or pump stations.

Waves
=====

The Waves tab couples SFINCS with the SnapWave spectral wave model for
nearshore wave transformation and wave-driven setup.

SnapWave Settings
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - SnapWave
     - Enable or disable the SnapWave wave model
     - ``snapwave``
   * - IG Waves
     - Enable infragravity wave computation
     - ``snapwave_igwaves``
   * - Time Step (s)
     - Time step for updating the wave field
     - ``dtwave``
   * - dTheta (deg)
     - Directional resolution in degrees
     - ``snapwave_dtheta``
   * - Nr Sweeps (-)
     - Maximum number of directional sweeps per time step
     - ``snapwave_nrsweeps``
   * - Crit (-)
     - Convergence criterion
     - ``snapwave_crit``
   * - Hmin (m)
     - Minimum depth for wave computation
     - ``snapwave_hmin``

Wave Boundary Conditions
------------------------

Wave boundary conditions define the incoming wave climate at the offshore
boundary of the SnapWave grid. Points are managed similarly to the water level
boundary points (add, delete, create along mesh, load/save).

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Distance (m)
     - Spacing between auto-generated wave boundary points
     - ``boundary_dx_snapwave``
   * - Wave Height (m)
     - Significant wave height Hm0
     - ``boundary_conditions_timeseries_hm0_snapwave``
   * - Wave Period (s)
     - Peak wave period Tp
     - ``boundary_conditions_timeseries_tp_snapwave``
   * - Wave Direction (deg)
     - Wave direction in nautical degrees (coming from)
     - ``boundary_conditions_timeseries_wd_snapwave``
   * - Wave Directional Spreading (deg)
     - Directional spreading
     - ``boundary_conditions_timeseries_ds_snapwave``

Wave Makers
-----------

Wave makers are polylines that generate waves inside the domain, typically
placed along the coastline. They should be drawn in counter-clockwise
direction (when looking at the coast from the water, draw from left to right).

Wave makers can be added interactively, imported from GeoJSON files, or loaded
from and saved to native file formats.

Meteo
=====

The Meteo tab defines the meteorological forcing applied to the model.

Forcing Type
------------

Select the type of meteorological input:

- **Uniform** -- spatially uniform wind and/or precipitation from ``.wnd`` and
  ``.prc`` files.
- **Spider web** -- cyclone wind and pressure fields from a ``.spw`` file.
- **Regular Grid** -- gridded wind and pressure from ``.amu``, ``.amv``, and
  ``.amp`` files.
- **Regular Grid + Spider web** -- combination of gridded background fields
  and a cyclone overlay.

Toggles
-------

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Wind
     - Enable or disable wind forcing
     - ``wind``
   * - Barometric Pressure
     - Enable or disable barometric pressure forcing
     - ``baro``
   * - Rain
     - Enable or disable rainfall forcing
     - ``rain``

File Selection
--------------

Depending on the forcing type, the following files can be selected:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - File
     - Description
     - Applicable Forcing Types
   * - Wind File (``.wnd``)
     - Uniform wind time series
     - Uniform
   * - AMU File (``.amu``)
     - Gridded u-component of wind
     - Regular Grid, Regular Grid + Spider web
   * - AMV File (``.amv``)
     - Gridded v-component of wind
     - Regular Grid, Regular Grid + Spider web
   * - AMP File (``.amp``)
     - Gridded atmospheric pressure
     - Regular Grid, Regular Grid + Spider web
   * - Precip File (``.prc``)
     - Uniform precipitation time series
     - Uniform
   * - AMPR File (``.ampr``)
     - Gridded precipitation
     - Regular Grid, Regular Grid + Spider web
   * - Spiderweb File (``.spw``)
     - Cyclone wind/pressure fields
     - Spider web, Regular Grid + Spider web

Observation Points
==================

The Observation Points tab has two sub-tabs for defining locations where model
output is recorded.

Points
------

Observation points are individual locations where time series of water level,
velocity, and other variables are stored at each output time step. Points can
be placed on the map, loaded from file, or saved.

Cross Sections
--------------

Cross sections are polylines across which integrated quantities (discharge,
cumulative volume) are computed. They are drawn on the map as polylines and can
be loaded from or saved to file.

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
   * - Restart output interval (s)
     - Interval for writing restart files
     - ``dtrstout``
   * - Output Format
     - File format: NetCDF, Binary, or ASCII
     - ``outputformat``
   * - Store Meteo
     - Include meteorological data in model output
     - ``storemeteo``
   * - Store Velocity
     - Include velocity fields in model output
     - ``storevel``
