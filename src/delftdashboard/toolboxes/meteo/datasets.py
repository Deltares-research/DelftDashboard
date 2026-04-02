"""GUI callbacks for the meteo datasets tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the datasets tab and update the map."""
    map.update()
    app.toolbox["meteo"].set_layer_mode("active")


def select_dataset(*args: Any) -> None:
    """Handle dataset selection change."""
    pass


def add_dataset(*args: Any) -> None:
    """Handle adding a new dataset."""
    pass


def select_source(*args: Any) -> None:
    """Handle source selection change."""
    pass


def edit_bbox(*args: Any) -> None:
    """Handle bounding-box edit interaction."""
    pass
