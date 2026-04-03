SFINCS Model Maker
==================

The SFINCS Model Maker toolbox (``modelmaker_sfincs_hmt``) builds SFINCS
models from scratch using the HydroMT-SFINCS framework. It guides the user
through a step-by-step workflow: define the domain, optionally refine with a
quadtree mesh, assign bathymetry, configure roughness, set active and
boundary cell masks, and optionally generate sub-grid tables. The toolbox is
available when the SFINCS model is active.

Domain
------

Define the computational grid by drawing a bounding box on the map or by
entering coordinates manually.

Parameters
^^^^^^^^^^

X0
   X-coordinate of the grid origin.

Y0
   Y-coordinate of the grid origin.

MMax
   Number of grid cells in the M-direction.

NMax
   Number of grid cells in the N-direction.

dX
   Grid cell size in the X-direction.

dY
   Grid cell size in the Y-direction.

Rotation
   Grid rotation angle in degrees.

Actions
^^^^^^^

Draw Bounding Box
   Interactively draw the grid extent on the map.

Generate Grid
   Create the computational grid from the current parameters.

SnapWave (checkbox)
   Enable the SnapWave spectral wave model. When enabled, additional tabs
   for SnapWave active and boundary cell masks become available.

Sub-Grid Bathymetry (checkbox)
   Enable sub-grid bathymetry for higher resolution depth representation.
   When enabled, the Sub Grid tab becomes available.

Show Mask Polygons (checkbox)
   Toggle visibility of mask polygons on the map.

Read Set-up File
   Read model set-up from a YAML file.

Write Set-up File
   Write model set-up to a YAML file.

Build Model
   Build the complete model from the current set-up in one step.


Quadtree
--------

Define quadtree mesh refinement regions using polygons. Quadtree refinement
allows finer resolution in areas of interest while keeping coarser cells
elsewhere.

Parameters
^^^^^^^^^^

Refinement Polygons (listbox)
   List of defined refinement polygons.

Refinement Level (dropdown)
   Refinement level for the selected polygon. Each level halves the cell
   size.

Zmin
   Minimum elevation threshold for refinement within the polygon.

Zmax
   Maximum elevation threshold for refinement within the polygon.

Actions
^^^^^^^

Draw Polygon
   Interactively draw a refinement polygon on the map.

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

Select and combine bathymetry/topography datasets to assign bed levels to
the computational grid. Multiple datasets can be used with a priority
ordering (datasets higher in the list take precedence).

Parameters
^^^^^^^^^^

Available Datasets (listbox)
   Datasets available from the selected source.

Source (dropdown)
   Source of bathymetry/topography datasets (e.g. local, online).

Selected Datasets (listbox)
   Datasets chosen for use, listed in priority order.

Zmin (per dataset)
   Minimum elevation -- values below this are excluded for the dataset.

Zmax (per dataset)
   Maximum elevation -- values above this are excluded for the dataset.

Zmin (m) (global)
   Global minimum bed level used in the model bathymetry.

Zmax (m) (global)
   Global maximum bed level used in the model bathymetry.

Actions
^^^^^^^

Use Dataset ->
   Add the selected dataset to the priority list.

Remove
   Remove a dataset from the priority list.

Move Up / Move Down
   Reorder datasets in the priority list.

Load Polygon
   Load a polygon to spatially limit the area used for a dataset.

Generate Bathymetry
   Interpolate the selected datasets onto the computational grid.


Roughness
---------

Define spatially varying roughness using Manning's n values.

Parameters
^^^^^^^^^^

Manning Land
   Manning's n roughness value for land cells.

Manning Water
   Manning's n roughness value for water cells.

Manning Level
   Vertical level (m) used to distinguish land from water.


Mask Active Cells
-----------------

Control which grid cells are active (computed) using global elevation
thresholds and spatial polygons.

Global Panel
^^^^^^^^^^^^

Use Global (checkbox)
   Enable global elevation-based masking.

Zmin
   Minimum elevation for active cells.

Zmax
   Maximum elevation for active cells.

Include Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^

Force cells inside these polygons to be active, optionally filtered by
elevation.

Include Polygon list
   List of include polygons.

Draw Polygon / Delete Polygon / Load Polygon / Save Polygon
   Manage include polygons.

Zmin / Zmax
   Elevation range for included cells within the polygon.

Exclude Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^

Force cells inside these polygons to be inactive, optionally filtered by
elevation.

Exclude Polygon list
   List of exclude polygons.

Draw Polygon / Delete Polygon / Load Polygon / Save Polygon
   Manage exclude polygons.

Zmin / Zmax
   Elevation range for excluded cells within the polygon.

Actions
^^^^^^^

Update Mask
   Recompute the active cell mask from the current settings.

Cut Inactive Cells
   Permanently remove inactive cells from the grid to reduce file size.


Mask Boundary Cells
-------------------

Define which cells act as open boundaries using polygon-based selection.
Four boundary types are supported, each managed in its own panel.

Open Boundary Polygons
   Water level boundary cells driven by external forcing.

Downstream Boundary Polygons
   Downstream (outflow) boundary cells.

Neumann Boundary Polygons
   Neumann (gradient) boundary cells.

Outflow Boundary Polygons
   Outflow boundary cells.

Each panel provides:

Polygon list
   List of boundary polygons for that type.

Draw / Delete / Load / Save
   Manage boundary polygons.

Zmin / Zmax
   Elevation thresholds for boundary cell selection.

Actions
^^^^^^^

Update Mask
   Recompute the boundary cell mask from the current settings.

Cut Inactive Cells
   Permanently remove inactive cells from the grid.


Mask Active SnapWave
--------------------

Control which SnapWave grid cells are active. This tab is only available
when the SnapWave checkbox is enabled in the Domain tab. The layout mirrors
the Mask Active Cells tab with Global, Include Polygons, and Exclude
Polygons panels, each with Zmin/Zmax thresholds.

Actions
^^^^^^^

Update Mask
   Recompute the SnapWave active cell mask.

Cut Inactive Cells
   Remove inactive cells from the SnapWave grid.


Mask Boundary SnapWave
----------------------

Define SnapWave open and Neumann boundary cells using polygons. This tab is
only available when SnapWave is enabled.

Open Boundary Polygons
   SnapWave open boundary polygons with Zmin/Zmax thresholds.

Neumann Boundary Polygons
   SnapWave Neumann boundary polygons with Zmin/Zmax thresholds.

Actions
^^^^^^^

Update Mask
   Recompute the SnapWave boundary cell mask.

Cut Inactive Cells
   Remove inactive cells from the SnapWave grid.


Sub Grid
--------

Generate sub-grid lookup tables for high-resolution depth representation on
a coarser computational grid. This tab is only available when the Sub-Grid
Bathymetry checkbox is enabled in the Domain tab.

Parameters
^^^^^^^^^^

Nr Levels
   Number of vertical levels in the sub-grid tables.

Nr Pixels per Cell
   Number of sub-grid pixels per coarse computational cell.

Max dZ/dV
   Maximum rate of change of depth with volume.

Manning (max)
   Maximum Manning's n below the cut-off level. Prevents overestimation of
   roughness in river beds where roughness maps may not resolve smaller
   streams.

Manning Cut-off Level (m)
   Elevation below which the maximum Manning value is applied.

Zmax (m)
   Maximum bed level used in the sub-grid table.

Zmin (m)
   Minimum bed level used in the sub-grid table.

Actions
^^^^^^^

Generate
   Compute the sub-grid tables from the current settings and selected
   bathymetry datasets.
