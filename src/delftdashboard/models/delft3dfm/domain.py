"""GUI callbacks for the Delft3D-FM domain/grid tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate grid and mask layers when the domain tab is selected."""
    # De-activate() existing layers
    map.update()
    # Show the grid and mask
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask_include"].activate()
    app.map.layer[_MODEL].layer["mask_boundary"].activate()


def set_model_variables(*args: Any) -> None:
    """Copy GUI variable values into the domain input object."""
    app.model[_MODEL].set_input_variables()
