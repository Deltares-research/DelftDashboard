"""GUI callbacks for the bathymetry tab of the SFINCS HMT model-maker toolbox."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the bathymetry tab and display the grid layer.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()


def generate_bathymetry(*args: Any) -> None:
    """Generate bathymetry for the current SFINCS model grid.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].generate_bathymetry()


def edit(*args: Any) -> None:
    """Handle edit action (placeholder).

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    pass


def info(*args: Any) -> None:
    """Display bathymetry information (placeholder).

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    pass
