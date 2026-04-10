"""GUI callbacks for the roughness tab of the Delft3D-FM model maker toolbox (placeholder)."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_cht"


def select(*args: Any) -> None:
    """Activate the roughness tab and deactivate other layers."""
    map.update()


def draw_domain(*args: Any) -> None:
    """Draw the domain for roughness configuration (not yet implemented)."""
    toolbox = app.toolbox[_TB]
    pass
