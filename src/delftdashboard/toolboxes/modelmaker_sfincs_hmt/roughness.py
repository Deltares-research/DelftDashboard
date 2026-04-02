"""GUI callbacks for the roughness tab of the SFINCS HMT model-maker toolbox."""

from typing import Any

from delftdashboard.operations import map

_TB = "modelmaker_sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the roughness tab and deactivate existing map layers.

    Parameters
    ----------
    *args : Any
        Unused positional arguments passed by the GUI framework.
    """
    map.update()


def edit(*agrs: Any) -> None:
    """Handle edit action (placeholder).

    Parameters
    ----------
    *agrs : Any
        Unused positional arguments passed by the GUI framework.
    """
    pass
