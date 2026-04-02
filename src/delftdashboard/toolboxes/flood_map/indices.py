"""GUI callbacks for the flood map indices tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the indices tab and update map layers."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")


def generate_index_geotiff(*args: Any) -> None:
    """Generate an index GeoTIFF for the active model grid."""
    app.toolbox["flood_map"].generate_index_geotiff()
