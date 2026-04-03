Bathymetry Import
=================

The Bathymetry toolbox (``bathymetry``) provides functionality to import
bathymetric and topographic datasets into the DelftDashboard data catalog.
Imported datasets become available in the bathymetry selector used by all
Model Maker toolboxes.

Import
------

Import a bathymetry/topography file and register it as a dataset in the
local catalog.

File Selection
^^^^^^^^^^^^^^

File Format (dropdown)
   Select the input file format. Supported formats:

   - **GeoTIFF** -- georeferenced raster in TIFF format.
   - **NetCDF** -- CF-compliant netCDF files with gridded elevation data.
   - **XYZ** -- plain text files with x, y, z columns.

Select File
   Browse for and select the input data file.

Import As (radio buttons)
   Choose how to store the imported data:

   - **Cloud Optimized GeoTIFF (COG)** -- converts to COG for efficient
     tiled access.
   - **Tiles** -- splits data into a tile pyramid for large datasets.

Variables (dropdown)
   For NetCDF files, select which variable contains the elevation data.

Metadata
^^^^^^^^

Name
   Short dataset name (no spaces or special characters except underscore).

Long Name
   Descriptive dataset name (may contain spaces and special characters).

Source
   Data source attribution.

Vertical Datum
   Vertical reference datum of the data.

Vertical Units
   Units of the vertical coordinate.

Difference with M.S.L.
   Offset from Mean Sea Level in the specified vertical units.

Actions
^^^^^^^

Import
   Process the selected file and add it to the local data catalog.
   Enabled only after a file has been selected.


Export
------

Export dataset to file.

Actions
^^^^^^^

Export
   Export the current dataset (currently disabled in the GUI).
