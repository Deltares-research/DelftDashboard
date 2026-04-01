"""GUI callbacks for the HurryWave Model Maker Wave Blocking tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Wave Blocking tab."""
    map.update()


def edit(*args: Any) -> None:
    """Handle wave blocking field edits (not yet implemented)."""


def generate_waveblocking(*args: Any) -> None:
    """Trigger wave blocking file generation."""
    app.toolbox[_TB].generate_waveblocking()
