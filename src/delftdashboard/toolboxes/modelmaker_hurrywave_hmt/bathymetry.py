"""GUI callbacks for the HurryWave Model Maker Bathymetry tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Bathymetry tab."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()


def generate_bathymetry(*args: Any) -> None:
    """Trigger bathymetry generation from selected datasets."""
    app.toolbox[_TB].generate_bathymetry()


def edit(*args: Any) -> None:
    """Handle bathymetry field edits (not yet implemented)."""


def info(*args: Any) -> None:
    """Show dataset information (not yet implemented)."""
