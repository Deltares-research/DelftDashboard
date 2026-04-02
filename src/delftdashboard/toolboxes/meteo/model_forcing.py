"""GUI callbacks for the meteo model forcing tab."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the model forcing tab and update the map."""
    map.update()
    app.toolbox["meteo"].set_layer_mode("active")


def select_dataset(*args: Any) -> None:
    """Handle dataset selection change."""
    pass


def edit_time(*args: Any) -> None:
    """Handle time range editing."""
    pass


def generate_model_forcing_files(*args: Any) -> None:
    """Collect meteo data and write Delft3D forcing files."""
    dataset_name = app.gui.getvar("meteo", "selected_dataset")
    tstart = app.gui.getvar("meteo", "tstart")
    tend = app.gui.getvar("meteo", "tstop")
    dataset = app.meteo_database.dataset[dataset_name]
    wb = app.gui.window.dialog_wait("Collecting meteo data ...")
    dataset.collect([tstart, tend])
    wb.close()
    # Make cut-out for area of interest
    # ds.cutout()
    wb = app.gui.window.dialog_wait("Writing forcing files ...")
    dataset.to_delft3d("sfincs")
    wb.close()
