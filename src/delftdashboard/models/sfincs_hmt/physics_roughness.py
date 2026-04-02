"""GUI callbacks for the SFINCS HydroMT Physics Roughness sub-tab.

Handles tab selection and synchronization of bed roughness
GUI variables with the model configuration.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Roughness sub-tab and update map layers."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()
