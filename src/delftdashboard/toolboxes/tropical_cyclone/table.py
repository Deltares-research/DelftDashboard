"""GUI callbacks for the tropical cyclone table tab.

Handle cyclone track data table editing and display.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the table tab and show cyclone layers."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")


def edit_table(*args: Any) -> None:
    """Edit the cyclone track data table (placeholder)."""
