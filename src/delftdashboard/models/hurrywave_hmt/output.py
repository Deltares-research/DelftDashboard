"""GUI callbacks for the HurryWave Output tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Output tab."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()
