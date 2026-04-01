"""GUI callbacks for the HurryWave Domain tab.

Handles tab selection and propagation of domain-related GUI variables
back to the HurrywaveModel configuration.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Domain tab and update map layers."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()
