"""GUI callbacks for the tropical cyclone import tab.

Handle track dataset selection, loading, saving, and deletion.
"""

from typing import Any

from cht_cyclones import track_selector

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the import tab and show cyclone layers."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")


def select_dataset(*args: Any) -> None:
    """Handle dataset selection events (placeholder)."""


def select_track(*args: Any) -> None:
    """Open the track selector dialog and load the chosen cyclone track."""
    dataset_name = app.gui.getvar("tropical_cyclone", "selected_track_dataset")
    dataset = app.toolbox["tropical_cyclone"].cyclone_track_database.get_dataset(
        dataset_name
    )

    center = app.map.map_center

    tc, okay = track_selector(
        dataset,
        app,
        lon=center[0],
        lat=center[1],
        distance=300.0,
        year_min=2000,
        year_max=2025,
    )

    if okay:
        app.toolbox["tropical_cyclone"].tc = tc
        app.toolbox["tropical_cyclone"].tc.name = app.toolbox[
            "tropical_cyclone"
        ].tc.name.lower()
        app.toolbox["tropical_cyclone"].track_added()


def load_track(*args: Any) -> None:
    """Load a cyclone track from file."""
    app.toolbox["tropical_cyclone"].load_track()


def save_track(*args: Any) -> None:
    """Save the current cyclone track to file."""
    app.toolbox["tropical_cyclone"].save_track()


def delete_track(*args: Any) -> None:
    """Delete the current cyclone track."""
    app.toolbox["tropical_cyclone"].delete_track()
