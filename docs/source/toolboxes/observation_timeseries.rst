Observation Timeseries
======================

The Observation Timeseries toolbox (``observation_timeseries``) loads one or
more SFINCS his (point output) netCDF files, plots the observation-point
locations on the map, and lets you build a comparison of station timeseries in
a standalone plot window. Timeseries are shown only in that window (never on
the map). Several his files can be loaded to compare output for the same
(identical) observation points.

The toolbox has three panels.

His files
---------

Load His File
   Open a SFINCS his (``*.nc``) file. The first file loaded defines the
   reference set of observation points, which are drawn on the map. Additional
   files must have the same number of observation points.

Delete / Clear
   Delete removes the selected his file; Clear unloads all files and empties
   the plot.

Label / Rename
   Give the selected file a custom legend label used when it is plotted.

Select station
--------------

Stations (list)
   Select an observation point by name. You can also click a point on the map
   to select it (this only highlights it - it does not plot).

Variable
   Choose which variable is used when adding a station to the plot:

   - **Water level** -- ``point_zs``.
   - **Water depth** -- ``point_h``.

Add to Plot
   Copy the selected station's timeseries (for the selected file and variable)
   into the plot window. The series is listed in the Plotted panel and drawn in
   the window. Re-adding the same station/file/variable refreshes its line.

Plotted
-------

Plotted (list)
   The series currently drawn in the plot window.

Remove
   Remove the selected series from the plot.

New Plot
   Start a fresh, empty plot window. Closing the window also clears the plot.

Expected file format
-------------------

The toolbox reads standard SFINCS his output, which contains ``point_zs`` /
``point_h`` with dimensions ``(time, stations)``, ``point_x`` / ``point_y``
station coordinates and a ``crs`` variable with an ``epsg_code`` attribute
(coordinates are reprojected to lon/lat for display), ``station_name`` and
``time``.
