"""GUI callbacks for the tropical cyclone wind field tab.

Handle wind field variable editing, spiderweb generation, and config I/O.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the wind field tab and show cyclone layers."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")


def edit_variables(*args: Any) -> None:
    """Handle wind field variable edit events (placeholder)."""


def build_spiderweb(*args: Any) -> None:
    """Generate the spiderweb wind field file."""
    app.toolbox["tropical_cyclone"].build_spiderweb()


def load_config(*args: Any) -> None:
    """Load wind field configuration from file."""
    app.toolbox["tropical_cyclone"].load_config()


def save_config(*args: Any) -> None:
    """Save wind field configuration to file."""
    app.toolbox["tropical_cyclone"].save_config()
