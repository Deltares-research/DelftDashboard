HurryWave Model Maker
=====================

The HurryWave Model Maker toolbox (``modelmaker_hurrywave_hmt``) builds
HurryWave spectral wave models from scratch using the HydroMT-HurryWave
framework. The workflow mirrors the SFINCS Model Maker: define the domain,
optionally refine with a quadtree mesh, assign bathymetry, set active and
boundary cell masks, and optionally generate wave blocking tables.

Domain
------

Define the computational grid by drawing a layout on the map or by entering
coordinates manually.

Parameters
^^^^^^^^^^

X0
   X-coordinate of the grid origin.

Y0
   Y-coordinate of the grid origin.

MMax
   Number of grid cells in the X-direction.

NMax
   Number of grid cells in the Y-direction.

dX
   Grid cell size in the X-direction.

dY
   Grid cell size in the Y-direction.

Rotation
   Grid rotation angle in degrees.

Actions
^^^^^^^

Draw Layout
   Interactively draw the grid outline on the map.

Generate Grid
   Create the computational grid from the current parameters.

Read Set-up File
   Read model set-up from a YAML file.

Write Set-up File
   Write model set-up to a YAML file.

Build Model
   Build the complete model (grid, bathymetry, mask, wave blocking) in one
   step.


Quadtree
--------

Define quadtree mesh refinement regions using polygons. Each polygon is
assigned a refinement level and optional elevation thresholds.

Parameters
^^^^^^^^^^

Refinement Polygons (listbox)
   List of defined refinement polygons.

Refinement Level (dropdown)
   Refinement level for the selected polygon.

Zmin
   Minimum elevation for refinement within the polygon.

Zmax
   Maximum elevation for refinement within the polygon.

Actions
^^^^^^^

Draw Polygon
   Draw a refinement polygon on the map.

Delete Polygon
   Remove the selected refinement polygon.

Load Polygons
   Load refinement polygons from a GeoJSON file.

Save Polygons
   Save refinement polygons to a GeoJSON file.

Generate Quadtree Mesh
   Build the quadtree grid using the defined refinement polygons.


Bathymetry
----------

Select and combine bathymetry/topography datasets with priority ordering.
The interface is shared with the SFINCS Model Maker and provides the same
source selection, dataset picker, Zmin/Zmax per dataset, and reordering
controls.

Parameters
^^^^^^^^^^

Available Datasets / Source
   Browse and select datasets from configured sources.

Selected Datasets
   Priority-ordered list of datasets to use.

Zmin / Zmax (per dataset)
   Elevation range filter for each dataset.

Zmin (m) / Zmax (m) (global)
   Global bed level limits for the final bathymetry.

Actions
^^^^^^^

Use Dataset -> / Remove / Move Up / Move Down
   Manage the priority list.

Load Polygon
   Spatially limit a dataset with a polygon.

Generate Bathymetry
   Interpolate selected datasets onto the grid.


Mask Active Cells
-----------------

Control which grid cells are active using global elevation thresholds and
include/exclude polygons.

Global Panel
^^^^^^^^^^^^

Zmin
   Minimum elevation for active cells.

Zmax
   Maximum elevation for active cells.

Include Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^

Force cells inside these polygons to be active, optionally filtered by
Zmin/Zmax.

Exclude Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^

Force cells inside these polygons to be inactive, optionally filtered by
Zmin/Zmax.

Actions
^^^^^^^

Update Mask
   Recompute the active cell mask.

Cut Inactive Cells
   Remove inactive cells from the grid.


Mask Boundary Cells
-------------------

Define open boundary cells using polygons with elevation thresholds.

Boundary Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^^

Boundary Polygon list
   List of open boundary polygons.

Draw Polygon / Delete Polygon / Load Polygon / Save Polygon
   Manage boundary polygons.

Zmin / Zmax
   Elevation range for boundary cell selection.

Actions
^^^^^^^

Update Mask
   Recompute the boundary cell mask.

Cut Inactive Cells
   Remove inactive cells from the grid.

Boundary Points
^^^^^^^^^^^^^^^

After the boundary mask is set, boundary points can be created along the
open boundary at a specified spacing.

Create Boundary Points
   Generate equally spaced boundary points along the open boundary.

Distance (m)
   Spacing between boundary points in metres.


Wave Blocking
-------------

Generate wave blocking tables that account for sheltering effects of
islands and other obstructions on wave propagation. This tab is only visible
when wave blocking is enabled.

Parameters
^^^^^^^^^^

Nr Dirs
   Number of directional bins in the wave blocking table. This must match
   ``ntheta`` in the HurryWave model settings (read-only in the GUI).

Nr Pixels per Cell
   Number of sub-grid pixels per computational cell used to resolve
   blocking features.

Z Threshold
   Minimum bed elevation (m) above which features are considered blocking.

Actions
^^^^^^^

Generate
   Compute the wave blocking table. One or more bathymetry datasets must be
   selected before generating.
