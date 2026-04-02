"""GUI callbacks for the Delft3D-FM generic settings tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Deactivate existing layers when the generic tab is selected."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Copy GUI variable values into the domain input object."""
    app.model[_MODEL].set_input_variables()
