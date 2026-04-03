Flood Map
=========

The Flood Map toolbox (``flood_map``) provides tools for preparing,
viewing, comparing, and exporting flood inundation maps from SFINCS model
output. It works with tiled GeoTIFF files for efficient visualization of
large domains.

Prepare
-------

Load the required input files before viewing flood maps.

Actions
^^^^^^^

Load Topo/Bathy GeoTiff
   Load a topography/bathymetry Cloud Optimized GeoTIFF (COG) file that
   provides the ground surface for computing flood depths.

Load Index GeoTiff
   Load an index GeoTIFF (COG) file that maps each pixel to a SFINCS
   computational cell.

Load Map Output
   Load SFINCS map output in netCDF format containing water level time
   series for each cell.


View
----

Visualize flood maps at individual time steps or as a maximum envelope.

Display Mode
^^^^^^^^^^^^

Instantaneous / Maximum (radio buttons)
   Toggle between viewing a single time step or the maximum flood extent
   over the entire simulation.

Time (listbox)
   Select the time step to display (only active in Instantaneous mode).

Color Settings
^^^^^^^^^^^^^^

Opacity (dropdown)
   Set the transparency level of the flood map overlay (0--100%).

Continuous / Discrete (radio buttons)
   Choose between smooth continuous colors or stepped discrete color bands.

Color Map (dropdown)
   Select the color map (e.g. viridis, plasma, jet).

Min value (m)
   Lower bound of the color scale.

Max value (m)
   Upper bound of the color scale.

Actions
^^^^^^^

Export
   Export the current flood map view to a GeoTIFF or netCDF file.


Compare
-------

Compare two flood map results side by side. This tab is a placeholder for
future development.


Topo/Bathy
-----------

Generate a topography/bathymetry GeoTIFF from selected datasets, for use
with the flood map viewer.

Parameters
^^^^^^^^^^

The tab includes the shared bathymetry/topography dataset selector
(Available Datasets, Selected Datasets, source dropdown, Zmin/Zmax per
dataset, and reordering controls).

Draw Polygon
   Draw a polygon to limit the spatial extent of the output GeoTIFF.

Delete Polygon
   Remove the extent polygon.

dX
   Grid resolution of the output GeoTIFF (in metres for projected CRS, in
   degrees for geographic CRS).

Actions
^^^^^^^

Generate Topo/Bathy GeoTiff
   Create a Cloud Optimized GeoTIFF from the selected datasets and polygon
   extent.


Indices
-------

Generate an index GeoTIFF that maps each raster pixel to a SFINCS
computational cell.

Actions
^^^^^^^

Generate Index GeoTiff
   Create the index GeoTIFF file for the current model domain.
