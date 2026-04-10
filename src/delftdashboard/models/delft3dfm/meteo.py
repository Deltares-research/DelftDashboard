"""GUI callbacks for the Delft3D-FM meteorological forcing tab."""

import ast
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Deactivate existing layers when the meteo tab is selected."""
    map.update()


def set_model_variables(*args: Any) -> None:
    """Parse string-encoded breakpoint lists and copy GUI values to the domain."""
    # Convert string list to list
    vars = ["wind.cdbreakpoints", "wind.windspeedbreakpoints"]
    for i, v in enumerate(vars):
        if isinstance(app.gui.variables[_MODEL][v]["value"], str):
            app.gui.variables[_MODEL][v]["value"] = ast.literal_eval(
                app.gui.variables[_MODEL][v]["value"]
            )

    app.model[_MODEL].set_input_variables()
