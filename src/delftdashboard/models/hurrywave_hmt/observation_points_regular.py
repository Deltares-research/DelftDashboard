"""GUI callbacks for HurryWave regular observation points.

Handles adding, deleting, loading, and saving observation points that
record time-series output (Hm0, Tp, etc.) at specific locations.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_GROUP = "hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args: Any) -> None:
    """Activate the Regular observation points tab."""
    map.update()
    app.map.layer[_MODEL].layer["observation_points_regular"].activate()
    update()


def edit(*args: Any) -> None:
    """Handle edits to observation-point fields."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Load observation points from a file."""
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="hurrywave.obs",
        filter="*.obs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.read()
        gdf = app.model[_MODEL].domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, 0)
        app.gui.setvar(_GROUP, "active_observation_point_regular", 0)
        update()


def save(*args: Any) -> None:
    """Save observation points to a file."""
    map.reset_cursor()
    file_name = app.model[_MODEL].domain.config.get("obsfile")
    if not file_name:
        file_name = "hurrywave.obs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.obs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.write()


def update() -> None:
    """Refresh the observation-point name list in the GUI."""
    gdf = app.model[_MODEL].domain.observation_points.gdf
    names = list(gdf["name"].values) if len(gdf) > 0 else []
    app.gui.setvar(_GROUP, "observation_point_names_regular", names)
    app.gui.setvar(_GROUP, "nr_observation_points_regular", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args: Any) -> None:
    """Start map click interaction to add a new observation point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add an observation point at *(x, y)*.

    Parameters
    ----------
    x, y : float
        Coordinates of the clicked location.
    """
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        return
    if name in app.gui.getvar(_GROUP, "observation_point_names_regular"):
        app.gui.window.dialog_info(
            "An observation point with this name already exists !"
        )
        return
    app.model[_MODEL].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points.gdf
    app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    update()


def select_observation_point_from_list(*args: Any) -> None:
    """Sync the map selection when a point is picked from the list."""
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_regular")
    app.map.layer[_MODEL].layer["observation_points_regular"].select_by_index(index)


def select_observation_point_from_map_regular(*args: Any) -> None:
    """Sync the GUI list when a point is picked on the map.

    Parameters
    ----------
    *args
        First element is a dict with an ``'id'`` key (feature index).
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    app.gui.window.update()


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected observation point."""
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_regular")
    app.model[_MODEL].domain.observation_points.delete([index])
    gdf = app.model[_MODEL].domain.observation_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    update()
