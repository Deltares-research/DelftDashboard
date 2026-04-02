"""Drawing toolbox for DelftDashboard.

Provides interactive polygon and polyline drawing, buffering,
merging, and file I/O on the map.
"""

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox


class Toolbox(GenericToolbox):
    """Toolbox for interactive polygon and polyline drawing."""

    def __init__(self, name: str) -> None:
        """Initialize the drawing toolbox.

        Parameters
        ----------
        name : str
            Name identifier for the toolbox.
        """
        super().__init__()
        self.name = name
        self.long_name = "Drawing"

    def initialize(self) -> None:
        """Set up default GUI variables for polygon and polyline drawing."""
        group = "drawing"
        app.gui.setvar(group, "nr_polygons", 0)
        app.gui.setvar(group, "polygon_names", [])
        app.gui.setvar(group, "active_polygon", 0)
        app.gui.setvar(group, "polygon_buffer_distance", 0.0)
        app.gui.setvar(group, "polygon_simplify_distance", 0.0)

        app.gui.setvar(group, "nr_polylines", 0)
        app.gui.setvar(group, "polyline_names", [])
        app.gui.setvar(group, "active_polyline", 0)
        app.gui.setvar(group, "polyline_buffer_distance", 0.0)
        app.gui.setvar(group, "polyline_simplify_distance", 0.0)
        app.gui.setvar(group, "polyline_buffer_distance_left", 0.0)
        app.gui.setvar(group, "polyline_buffer_distance_right", 0.0)
        app.gui.setvar(group, "polyline_parallel_offset_distance", 0.0)

        self.polygon = gpd.GeoDataFrame()
        self.polyline = gpd.GeoDataFrame()

        self.polygon_file_name = "polygon.geojson"
        self.polyline_file_name = "polyline.geojson"
        self.shifted_polyline_file_name = "shifted_polylines.geojson"

        self.asymmetric_buffer = False

    def add_layers(self) -> None:
        """Register map layers for polygon and polyline drawing."""
        layer = app.map.add_layer("drawing")
        from .polygon import polygon_created, polygon_modified, polygon_selected

        layer.add_layer(
            "polygon",
            type="draw",
            shape="polygon",
            create=polygon_created,
            modify=polygon_modified,
            select=polygon_selected,
        )
        layer.add_layer(
            "polygon_tmp",
            type="polygon",
            line_color="white",
            line_style="--",
        )
        from .polyline import polyline_created, polyline_modified, polyline_selected

        layer.add_layer(
            "polyline",
            type="draw",
            shape="polyline",
            create=polyline_created,
            modify=polyline_modified,
            select=polyline_selected,
        )
        layer.add_layer(
            "polyline_tmp",
            type="polygon",
            line_color="white",
            line_style="--",
        )
        layer.add_layer(
            "polyline_asym_tmp",
            type="polygon",
            line_color="yellow",
            line_style="--",
        )
        layer.add_layer(
            "polyline_parallel_offset_tmp",
            type="line",
            line_color="white",
            line_style=":",
        )

    def plot(self) -> None:
        """Plot drawing layers (placeholder)."""

    def set_layer_mode(self, mode: str) -> None:
        """Control visibility of drawing layers.

        Parameters
        ----------
        mode : str
            One of ``"active"``, ``"inactive"``, or ``"invisible"``.
        """
        if mode == "inactive":
            app.map.layer["drawing"].hide()
            app.map.layer["drawing"].layer["polygon"].hide()
            app.map.layer["drawing"].layer["polygon_tmp"].hide()
            app.map.layer["drawing"].layer["polyline"].hide()
            app.map.layer["drawing"].layer["polyline_tmp"].hide()
            app.map.layer["drawing"].layer["polyline_asym_tmp"].hide()
            app.map.layer["drawing"].layer["polyline_parallel_offset_tmp"].hide()
        elif mode == "invisible":
            app.map.layer["drawing"].hide()
            app.map.layer["drawing"].layer["polygon"].hide()
            app.map.layer["drawing"].layer["polygon_tmp"].hide()
            app.map.layer["drawing"].layer["polyline"].hide()
            app.map.layer["drawing"].layer["polyline_tmp"].hide()
            app.map.layer["drawing"].layer["polyline_asym_tmp"].hide()
            app.map.layer["drawing"].layer["polyline_parallel_offset_tmp"].hide()
        else:
            app.map.layer["drawing"].show()
