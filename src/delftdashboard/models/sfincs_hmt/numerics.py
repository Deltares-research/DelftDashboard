"""GUI callbacks for the SFINCS HydroMT Numerics tab.

Handles tab selection and synchronization of numerical scheme
GUI variables with the model configuration.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Numerics tab and update map layers."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


# def set_theta(*args):
#     pass
#     #    models.model["sfincs"].set_model_variables()
#     #    # OR:
#     app.model["sfincs_hmt"].domain.input.theta = app.gui.variables.var["sfincs"]["theta"]["value"]
