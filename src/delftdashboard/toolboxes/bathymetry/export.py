"""GUI callbacks for the bathymetry export tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the export tab."""
    map.update()


def export_dataset(*args: Any) -> None:
    """Export the current bathymetry dataset."""
    app.toolbox["bathymetry"].export_dataset()
