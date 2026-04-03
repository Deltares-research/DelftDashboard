Drawing
=======

The Drawing toolbox (``drawing``) provides general-purpose tools for
creating and manipulating polylines and polygons on the map. These shapes
can be used as input for other toolboxes (e.g. mask polygons, refinement
regions) or exported for external use.

Polyline
--------

Create and edit polylines on the map.

Polyline Management
^^^^^^^^^^^^^^^^^^^

Polylines (listbox)
   List of available polylines.

Add Polyline
   Draw a new polyline interactively on the map.

Delete Polyline
   Remove the selected polyline.

Load Polyline
   Load polylines from a GeoJSON file.

Save Polyline
   Save polylines to a GeoJSON file.

Buffer Operations
^^^^^^^^^^^^^^^^^

Apply Buffer
   Create a polygon by applying a symmetric buffer around the selected
   polyline(s). The resulting polygon appears under the Polygon tab.

Distance (m)
   Buffer distance in metres.

Apply Asymmetric Buffer
   Create a polygon using different distances on the left and right sides
   of the polyline.

Distance left (m)
   Buffer distance on the left side of the polyline (in metres).

Distance right (m)
   Buffer distance on the right side of the polyline (in metres).

Apply Parallel Offset
   Create a new polyline offset from the selected one by a specified
   distance.

Distance (m)
   Offset distance in metres. Negative values offset to the left, positive
   values to the right.


Polygon
-------

Create and edit polygons on the map.

Polygon Management
^^^^^^^^^^^^^^^^^^

Polygons (listbox)
   List of available polygons.

Add Polygon
   Draw a new polygon interactively on the map.

Delete Polygon
   Remove the selected polygon.

Load Polygon
   Load polygons from a GeoJSON file.

Save Polygon
   Save polygons to a GeoJSON file.

Operations
^^^^^^^^^^

Apply Buffer
   Adjust the selected polygon by applying a buffer (positive expands,
   negative shrinks).

Distance (m)
   Buffer distance in metres.

Merge Polygons
   Merge all polygons into a single polygon. Only enabled when more than
   one polygon exists.
