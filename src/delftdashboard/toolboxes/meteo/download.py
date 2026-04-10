"""GUI callbacks for the meteo download tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the download tab and update the map."""
    map.update()
    app.toolbox["meteo"].set_layer_mode("active")


def select_dataset(*args: Any) -> None:
    """Handle dataset selection change."""
    pass


def edit_time(*args: Any) -> None:
    """Handle time range editing."""
    pass


def download(*args: Any) -> None:
    """Download meteo data for the selected dataset and time range."""
    dataset_name = app.gui.getvar("meteo", "selected_dataset")
    tstart = app.gui.getvar("meteo", "tstart")
    tend = app.gui.getvar("meteo", "tstop")
    dataset = app.meteo_database.dataset[dataset_name]
    wb = app.gui.window.dialog_wait("Downloading meteo data ...")
    dataset.download([tstart, tend])
    wb.close()
