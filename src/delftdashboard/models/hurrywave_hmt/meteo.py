"""GUI callbacks for the HurryWave Meteo tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Meteo tab."""
    map.update()


def edit(*args: Any) -> None:
    """Handle edits to meteo input fields."""
    app.model[_MODEL].set_model_variables()
