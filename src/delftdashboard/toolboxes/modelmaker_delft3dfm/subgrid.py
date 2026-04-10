"""GUI callbacks for the subgrid tab of the Delft3D-FM model maker toolbox (placeholder)."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_cht"


def select(*args: Any) -> None:
    """Activate the subgrid tab and deactivate other layers."""
    map.update()


def edit(*args: Any) -> None:
    """Edit subgrid settings (not yet implemented)."""
    pass


def generate_subgrid(*args: Any) -> None:
    """Generate the subgrid tables."""
    app.toolbox[_TB].generate_subgrid()
