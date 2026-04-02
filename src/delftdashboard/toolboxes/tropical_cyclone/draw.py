"""GUI callbacks for the tropical cyclone draw tab.

Handle track drawing and visualization on the map.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the draw tab and show the cyclone track layer."""
    map.update()
    app.map.layer["tropical_cyclone"].layer["cyclone_track"].show()


def draw_track(*args: Any) -> None:
    """Draw a tropical cyclone track on the map (placeholder)."""
