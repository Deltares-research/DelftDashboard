==========
Delft3D-FM
==========

Overview
========

Delft3D Flexible Mesh (Delft3D-FM) is a full 2D/3D hydrodynamic model that
solves the shallow water equations on an unstructured (flexible) mesh. It
supports tidal flow, storm surge, river discharge, salinity transport, and wind-
driven circulation. The flexible mesh allows local refinement in areas of
interest while keeping the overall computational cost manageable.

In DelftDashboard the Delft3D-FM model can be configured through the GUI panels
described below. Grid generation and bathymetry interpolation are handled by the
Model Maker toolbox.

Geometry
========

The Geometry tab is organized into four sub-tabs that define the computational
mesh and related spatial data.

Net
---

The Net sub-tab displays and manages the unstructured mesh (network). The mesh
can be generated externally or through the Model Maker toolbox.

Structures
----------

The Geometry > Structures sub-tab allows placement of hydraulic structures
(weirs, gates, etc.) that are embedded in the mesh geometry.

Initial Conditions
------------------

The Initial Conditions sub-tab defines the starting state of the simulation
(initial water levels, velocities, salinity, etc.).

Miscellaneous
-------------

The Miscellaneous sub-tab contains additional geometry-related settings such as
dry points and fixed weirs.

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
     - Reference date and time for the simulation
     - ``time.refdate``
   * - Start Time
     - Simulation start date and time
     - ``time.tstart``
   * - Stop Time
     - Simulation stop date and time
     - ``time.tstop``

Physics
=======

The Physics tab contains sub-panels for physical process parameters.

Constants
---------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Horizontal Eddy Viscosity (m2/s)
     - Horizontal eddy viscosity coefficient
     - ``physics.vicouv``
   * - Vertical Eddy Viscosity (m2/s)
     - Vertical eddy viscosity coefficient
     - ``physics.vicoww``
   * - Vertical Eddy Diffusivity (m2/s)
     - Vertical eddy diffusivity coefficient
     - ``physics.dicoww``
   * - Smagorinsky
     - Smagorinsky coefficient for horizontal turbulence
     - ``physics.smagorinsky``
   * - Average Water Density (kg/m3)
     - Mean water density
     - ``physics.rhomean``
   * - Tidal Forcing
     - Enable or disable equilibrium tidal forcing
     - ``physics.tidalforcing``
   * - Salinity
     - Enable or disable salinity transport
     - ``physics.salinity``
   * - Secondary Flow
     - Enable or disable secondary flow computation
     - ``physics.secondaryflow``

Roughness
---------

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Uniform Friction Coefficient
     - Spatially uniform bottom friction value
     - ``physics.uniffrictcoef``
   * - Friction Type
     - Bottom friction formulation: Chezy, Manning, White-Colebrook, or z0
     - ``physics.uniffricttype``

Numerics
========

The Numerics tab controls the numerical scheme settings.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - CFL Max
     - Maximum Courant number
     - ``numerics.cflmax``
   * - Advection Type
     - Advection scheme: no advection, Perot q(uio-u) fast, or Perot q(ui-u)
     - ``numerics.advectype``

Boundary Conditions
===================

The Boundary Conditions tab provides two approaches for specifying water level
boundaries.

Tide Model Generation
---------------------

Generate tidal boundary conditions from a global tide model. Select a tide
model from the drop-down and press *Generate WL From Tide Model*.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Tide Model
     - Global tide model for constituent extraction
     - ``boundary_conditions_tide_model``
   * - Offset (m)
     - Water level offset in metres
     - ``boundary_conditions_tide_offset``

Custom Signal Generation
------------------------

Generate custom water level time series for all boundary points using a
parametric signal shape.

.. list-table::
   :header-rows: 1
   :widths: 25 55 20

   * - Parameter
     - Description
     - Variable
   * - Shape
     - Signal shape: Constant, Gaussian, or Sinusoidal
     - ``boundary_conditions_timeseries_shape``
   * - Time Step (s)
     - Time step for the generated time series
     - ``boundary_conditions_timeseries_time_step``
   * - Offset (m)
     - Water level offset in metres
     - ``boundary_conditions_timeseries_offset_custom``

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

Meteo
=====

The Meteo tab configures wind forcing for the model.

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Parameter
     - Description
     - Variable
   * - Wind Friction Type
     - Wind drag formulation: Constant, Smith and Banke (2 or 3 breakpoints), or Charnock
     - ``wind.icdtyp``
   * - Cd Breakpoints
     - Drag coefficient breakpoints (comma-separated list)
     - ``wind.cdbreakpoints``
   * - Wind Speed Breakpoints
     - Wind speed breakpoints in m/s (comma-separated list)
     - ``wind.windspeedbreakpoints``
   * - Air density (kg/m3)
     - Air density used in wind drag computation
     - ``wind.rhoair``
   * - Relative Wind Speed Factor
     - Factor for relative wind speed computation
     - ``wind.relativewind``

Observations
============

The Observations tab has two sub-tabs for defining output locations.

Points
------

Observation points are individual locations where time series of water level,
velocity, salinity, and other variables are recorded. Points can be placed on
the map, loaded from file, or saved.

Cross Sections
--------------

Cross sections are polylines across which discharge and other integrated
quantities are computed. They are drawn on the map and can be loaded from or
saved to file.

Structures
==========

The Structures tab allows placement of hydraulic structures.

Thin Dams
---------

Thin dams are infinitely thin barriers that block flow between adjacent cells.
They are defined as polylines drawn on the map. Typical uses include levees,
dikes, and road embankments that are narrower than a mesh cell.

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
     - ``output.mapinterval``
   * - His output interval (s)
     - Interval for writing time series at observation points
     - ``output.hisinterval``
   * - Restart output interval (s)
     - Interval for writing restart files
     - ``output.rstinterval``
