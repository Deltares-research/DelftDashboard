"""GUI callbacks for the flood map export tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the export tab and update map layers."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")


def export(*args: Any) -> None:
    """Export the current flood map to a file."""
    app.toolbox["flood_map"].export_flood_map()
