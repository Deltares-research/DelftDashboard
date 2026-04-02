"""GUI callbacks for the flood map compare tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the compare tab and update map layers."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")


def edit_table(*args: Any) -> None:
    """Handle table edit events (placeholder)."""
