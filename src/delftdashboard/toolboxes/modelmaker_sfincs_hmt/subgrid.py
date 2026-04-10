"""GUI callbacks for the sub-grid tab of the SFINCS HMT model-maker toolbox."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the sub-grid tab and deactivate existing map layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()


def edit(*args: Any) -> None:
    """Handle edit action (placeholder).

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    pass


def generate_subgrid(*args: Any) -> None:
    """Generate sub-grid tables for the current SFINCS model.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    app.toolbox[_TB].generate_subgrid()
