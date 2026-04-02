"""GUI callbacks for the tropical cyclone modify tab.

Handle cyclone track modification on the map.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the modify tab and show cyclone layers."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")


def modify(*args: Any) -> None:
    """Modify the tropical cyclone track (placeholder)."""
