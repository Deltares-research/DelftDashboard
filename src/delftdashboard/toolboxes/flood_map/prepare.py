"""GUI callbacks for the flood map prepare tab.

Handle loading topobathy/index GeoTIFFs and map output files.
"""

import os
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the prepare tab and update map layers."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")


def load_topobathy_geotiff(*args: Any) -> None:
    """Load a topobathy GeoTIFF and update the file label."""
    app.toolbox["flood_map"].load_topobathy_geotiff()
    fname = os.path.basename(app.toolbox["flood_map"].topobathy_geotiff)
    app.gui.setvar("flood_map", "topo_file_string", f"File : {fname}")


def load_index_geotiff(*args: Any) -> None:
    """Load an index GeoTIFF and update the file label."""
    app.toolbox["flood_map"].load_index_geotiff()
    fname = os.path.basename(app.toolbox["flood_map"].index_geotiff)
    app.gui.setvar("flood_map", "index_file_string", f"File : {fname}")


def load_map_output(*args: Any) -> None:
    """Load model map output and update the file label."""
    app.toolbox["flood_map"].load_map_output()
    fname = os.path.basename(app.toolbox["flood_map"].map_file_name)
    app.gui.setvar("flood_map", "map_file_string", f"File : {fname}")


def edit_table(*args: Any) -> None:
    """Handle table edit events (placeholder)."""
