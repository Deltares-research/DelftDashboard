Observation Timeseries
======================

The Observation Timeseries toolbox (``observation_timeseries``) loads one or
more SFINCS his (point output) netCDF files, plots the observation-point
locations on the map, and shows the timeseries for a point when you click it.
Several his files can be loaded at once to compare output for the same
(identical) observation points.

Loading data
------------

Load His File
   Open a SFINCS his (``*.nc``) file. The first file loaded defines the
   reference set of observation points, which are drawn on the map. Load
   additional files to compare runs; each additional file must have the same
   number of observation points as the first.

Clear
   Unload all his files and remove the points and popup from the map.

His files (list)
   The currently loaded files. Each file is drawn as a separate line in the
   timeseries plot.

Viewing timeseries
------------------

Stations (list)
   Select an observation point by name. This highlights it on the map and
   opens its timeseries popup.

Clicking a point
   Click any observation point on the map to open a timeseries popup anchored
   at that location. When several his files are loaded, one line is drawn per
   file (labelled by file name) so the runs can be compared directly.

Variable
   Choose which variable to plot:

   - **Water level** -- ``point_zs`` (sea surface height above reference).
   - **Water depth** -- ``point_h``.

Expected file format
-------------------

The toolbox reads standard SFINCS his output, which contains:

- ``point_zs`` / ``point_h`` with dimensions ``(time, stations)``,
- ``point_x`` / ``point_y`` station coordinates and a ``crs`` variable with an
  ``epsg_code`` attribute (coordinates are reprojected to lon/lat for display),
- ``station_name`` and ``time``.
