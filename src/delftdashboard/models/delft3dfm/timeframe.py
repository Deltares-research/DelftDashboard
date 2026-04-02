"""GUI callbacks for the Delft3D-FM timeframe settings tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Deactivate existing layers when the timeframe tab is selected."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Write GUI time variables into the domain timeframe attributes."""
    app.model[_MODEL].set_timeframe()
