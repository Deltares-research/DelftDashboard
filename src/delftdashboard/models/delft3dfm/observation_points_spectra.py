"""GUI callbacks for Delft3D-FM spectral observation point management."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the spectral observation points layer when the tab is selected."""
    map.update()
    app.map.layer[_MODEL].layer["observation_points_spectra"].activate()
    update()


def edit(*args: Any) -> None:
    """Apply GUI edits to the domain model variables."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Open a spectral observation point file via dialog and load it."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="delft3dfm.osp",
        filter="*.osp",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.variables.ospfile = rsp[2]
        app.model[_MODEL].domain.observation_points_sp2.read()
        gdf = app.model[_MODEL].domain.observation_points_sp2.gdf
        app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, 0)
        app.gui.setvar(_MODEL, "active_observation_point_spectra", 0)
        update()


def save(*args: Any) -> None:
    """Save spectral observation points to a user-selected file."""
    map.reset_cursor()
    file_name = app.model[_MODEL].domain.input.variables.ospfile
    if not file_name:
        file_name = "delft3dfm.osp"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.osp",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.input.variables.ospfile = rsp[2]
        app.model[_MODEL].domain.observation_points_sp2.write()


def update() -> None:
    """Refresh spectral observation point names and counts in the GUI."""
    gdf = app.active_model.domain.observation_points_sp2.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar(_MODEL, "observation_point_names_spectra", names)
    app.gui.setvar(_MODEL, "nr_observation_points_spectra", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args: Any) -> None:
    """Enable interactive point placement mode on the map."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a new spectral observation point.

    Parameters
    ----------
    x : float
        X-coordinate of the clicked location.
    y : float
        Y-coordinate of the clicked location.
    """
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        return
    if name in app.gui.getvar(_MODEL, "observation_point_names_spectra"):
        app.gui.window.dialog_info(
            "An observation point with this name already exists !"
        )
        return
    app.model[_MODEL].domain.observation_points_sp2.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points_sp2.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points_sp2.gdf
    app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar(_MODEL, "active_observation_point_spectra", index)
    update()


def select_observation_point_from_list(*args: Any) -> None:
    """Select the spectral observation point chosen in the GUI list on the map."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_observation_point_spectra")
    app.map.layer[_MODEL].layer["observation_points_spectra"].select_by_index(index)


def select_observation_point_from_map_spectra(*args: Any) -> None:
    """Handle selection of a spectral observation point by clicking on the map.

    Parameters
    ----------
    *args : Any
        Map callback arguments; ``args[0]["id"]`` holds the feature index.
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_MODEL, "active_observation_point_spectra", index)
    app.gui.window.update()


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected spectral observation point."""
    map.reset_cursor()
    index = app.gui.getvar(_MODEL, "active_observation_point_spectra")
    app.model[_MODEL].domain.observation_points_sp2.delete_point(index)
    gdf = app.model[_MODEL].domain.observation_points_sp2.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar(_MODEL, "active_observation_point_spectra", index)
    update()
