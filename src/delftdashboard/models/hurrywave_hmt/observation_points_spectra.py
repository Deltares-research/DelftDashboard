"""GUI callbacks for HurryWave spectral observation points.

Handles adding, deleting, loading, and saving observation points that
record 2-D spectral output at specific locations.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_GROUP = "hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Spectra observation points tab."""
    map.update()
    app.map.layer[_MODEL].layer["observation_points_spectra"].activate()
    update()


def edit(*args: Any) -> None:
    """Handle edits to observation-point fields."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Load spectral observation points from a file."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="hurrywave.osp",
        filter="*.osp",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("ospfile", rsp[2])
        app.model[_MODEL].domain.observation_points_spectra.read()
        gdf = app.model[_MODEL].domain.observation_points_spectra.gdf
        app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, 0)
        app.gui.setvar(_GROUP, "active_observation_point_spectra", 0)
        update()


def save(*args: Any) -> None:
    """Save spectral observation points to a file."""
    map.reset_cursor()
    file_name = app.model[_MODEL].domain.config.get("ospfile")
    if not file_name:
        file_name = "hurrywave.osp"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.osp",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("ospfile", rsp[2])
        app.model[_MODEL].domain.observation_points_spectra.write()


def update() -> None:
    """Refresh the spectral observation-point name list in the GUI."""
    gdf = app.model[_MODEL].domain.observation_points_spectra.gdf
    names = list(gdf["name"].values) if len(gdf) > 0 else []
    app.gui.setvar(_GROUP, "observation_point_names_spectra", names)
    app.gui.setvar(_GROUP, "nr_observation_points_spectra", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args: Any) -> None:
    """Start map click interaction to add a new spectral observation point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a spectral observation point at *(x, y)*.

    Parameters
    ----------
    x, y : float
        Coordinates of the clicked location.
    """
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        return
    if name in app.gui.getvar(_GROUP, "observation_point_names_spectra"):
        app.gui.window.dialog_info(
            "An observation point with this name already exists !"
        )
        return
    app.model[_MODEL].domain.observation_points_spectra.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points_spectra.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points_spectra.gdf
    app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_spectra", index)
    update()


def select_observation_point_from_list(*args: Any) -> None:
    """Sync the map selection when a point is picked from the list."""
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_spectra")
    app.map.layer[_MODEL].layer["observation_points_spectra"].select_by_index(index)


def select_observation_point_from_map_spectra(*args: Any) -> None:
    """Sync the GUI list when a point is picked on the map.

    Parameters
    ----------
    *args
        First element is a dict with an ``'id'`` key (feature index).
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_observation_point_spectra", index)
    app.gui.window.update()


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected spectral observation point."""
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_spectra")
    app.model[_MODEL].domain.observation_points_spectra.delete([index])
    gdf = app.model[_MODEL].domain.observation_points_spectra.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points_spectra"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_spectra", index)
    update()
