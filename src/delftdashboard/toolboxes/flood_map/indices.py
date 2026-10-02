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


def apply_structures_to_index(*args: Any) -> None:
    """Reassign pixels across the model's thin dams and weirs in the index GeoTIFF."""
    app.toolbox["flood_map"].apply_structures_to_index()
