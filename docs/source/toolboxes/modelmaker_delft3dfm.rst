Delft3D-FM Model Maker
======================

The Delft3D-FM Model Maker toolbox (``modelmaker_delft3dfm``) builds
Delft3D Flexible Mesh models. The workflow covers bathymetry assignment,
domain definition, grid refinement, open boundary generation, and cell
exclusion.

.. note::

   The tab order in the GUI places Bathymetry first, followed by Domain,
   Refinement, Boundary, and Exclude.


Bathymetry
----------

Select and combine bathymetry/topography datasets with priority ordering.
Uses the shared bathymetry/topography selector component.

Parameters
^^^^^^^^^^

Available Datasets / Source
   Browse and select datasets from configured sources.

Selected Datasets
   Priority-ordered list of datasets to use.

Zmin / Zmax (per dataset)
   Elevation range filter for each dataset.

Actions
^^^^^^^

Use Dataset -> / Remove / Move Up / Move Down
   Manage the priority list.

Load Polygon
   Spatially limit a dataset with a polygon.

Generate Bathymetry
   Interpolate selected datasets onto the grid.


Domain
------

Define the base computational grid.

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

Actions
^^^^^^^

Draw Layout
   Interactively draw the grid layout on the map.

Generate Grid
   Create the computational grid.

Read Set-up File
   Read model set-up from a YAML file.

Write Set-up File
   Write model set-up to a YAML file.

Build Model
   Build the complete model from the current set-up.


Refinement
----------

Refine the flexible mesh using polygons and/or depth-based criteria.

Refinement Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^^^^

Refinement Polygon list
   List of refinement polygons.

Min. edge size
   Minimum grid edge size (in metres) within the selected polygon.

Draw Polygon / Delete Polygon / Load Polygons / Save Polygons
   Manage refinement polygons.

Generate Grid Refinement Panel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Polygon Refinement
   Refine all cells inside the defined polygons.

Depth in Polygon Refinement
   Refine cells inside polygons based on local depth.

Depth Refinement
   Refine the entire grid based on depth, using the specified minimum edge
   size.

Min. edge size (global)
   Minimum grid edge size for depth-based refinement across the full
   domain.

Finalize Grid Panel
^^^^^^^^^^^^^^^^^^^

Connect Nodes
   After refinement is complete, connect hanging nodes to produce a valid
   mesh.


Boundary
--------

Define open boundary conditions using polygons or coastline data.

Open Boundary Polygon Panel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Boundary Polygon list
   List of open boundary polygons.

Draw Polygon / Delete Polygon / Load Polygon / Save Polygon
   Manage open boundary polygons.

Settings Panel
^^^^^^^^^^^^^^

Bnd resolution (m)
   Resolution of the boundary points along the open boundary (in metres).

Actions
^^^^^^^

Generate bnd from polygon
   Create boundary points from the drawn polygon.

Generate bnd from coastlines
   Automatically generate boundary points using a global coastline dataset.
   The open boundary is placed where the grid edge does not touch land.

Load bnd
   Load an existing boundary file.


Exclude
-------

Remove grid cells that should not be part of the computation.

Exclude Polygons Panel
^^^^^^^^^^^^^^^^^^^^^^

Exclude Polygon list
   List of exclude polygons.

Draw Polygon / Delete Polygon / Load Polygon / Save Polygon
   Manage exclude polygons.

Actions
^^^^^^^

Delete cells inside polygon
   Remove all cells that fall inside the drawn exclude polygons.

Delete cells based on coastline
   Automatically remove cells on land using a global coastline dataset.
