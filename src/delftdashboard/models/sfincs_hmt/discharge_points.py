"""GUI callbacks for the SFINCS HydroMT Discharge Points tab.

Handles adding, deleting, loading, and saving discharge point sources,
as well as map interaction for point selection and placement.
"""

from typing import Any

import pandas as pd

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Discharge Points tab and show points on map."""
    map.update()
    app.map.layer[_MODEL].layer["discharge_points"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved discharge point changes when leaving the tab."""
    if app.model[_MODEL].discharge_points_changed:
        ok = app.gui.window.dialog_yes_no(
            "The discharge points have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def edit(*args: Any) -> None:
    """Synchronize GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def load(*args: Any) -> None:
    """Load discharge points from .src and .dis files selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()

    # Always load both the src and dis file

    # Src file
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.src",
        filter="*.src",
        allow_directory_change=False,
    )

    # Src file
    if rsp[0]:
        app.model[_MODEL].domain.config.set("srcfile", rsp[2])
    else:
        return

    # Dis file
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.dis",
        filter="*.dis",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("disfile", rsp[2])
    else:
        return

    app.model[_MODEL].domain.discharge_points.read()
    gdf = app.model[_MODEL].domain.discharge_points.gdf
    app.map.layer[_MODEL].layer["discharge_points"].set_data(gdf, 0)
    app.gui.setvar(_GROUP, "active_discharge_point", 0)
    update()

    app.model[_MODEL].discharge_points_changed = False


def save(*args: Any) -> None:
    """Save discharge points to .src and .dis files selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()

    # Always save both the src and dis file

    # Src file
    filename = app.model[_MODEL].domain.config.get("srcfile")
    if not filename:
        filename = "sfincs.src"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.src",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("srcfile", rsp[2])
    else:
        return

    # Dis file
    filename = app.model[_MODEL].domain.config.get("disfile")
    if not filename:
        filename = "sfincs.dis"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.dis",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("disfile", rsp[2])
    else:
        return

    app.model[_MODEL].domain.discharge_points.write()

    app.model[_MODEL].discharge_points_changed = False


def update() -> None:
    """Refresh the discharge point name list in the GUI."""
    gdf = app.active_model.domain.discharge_points.gdf
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])
    app.gui.setvar(_GROUP, "discharge_point_names", names)
    app.gui.setvar(_GROUP, "nr_discharge_points", len(gdf))
    app.gui.window.update()


def add_discharge_point_on_map(*args: Any) -> None:
    """Start map click interaction to add a new discharge point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a discharge point at *(x, y)*.

    Parameters
    ----------
    x : float
        Longitude or x-coordinate of the clicked location.
    y : float
        Latitude or y-coordinate of the clicked location.
    """
    # Name
    name, okay = app.gui.window.dialog_string("Edit name for new discharge point")
    if not okay:
        # Cancel was clicked
        return
    if name in app.gui.getvar(_GROUP, "discharge_point_names"):
        app.gui.window.dialog_info("A discharge point with this name already exists !")
        return
    # Discharge
    qstr, okay = app.gui.window.dialog_string(
        "Edit discharge for new discharge point (m3/s)"
    )
    if not okay:
        # Cancel was clicked
        return
    # Try to convert qstr to float
    try:
        q = float(qstr)
    except Exception:
        app.gui.window.dialog_info("Invalid discharge value !")
        return
    app.model[_MODEL].domain.discharge_points.add_point(x, y, name=name, value=q)
    index = len(app.model[_MODEL].domain.discharge_points.gdf) - 1
    gdf = app.model[_MODEL].domain.discharge_points.gdf
    app.map.layer[_MODEL].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_discharge_point", index)
    update()
    app.model[_MODEL].discharge_points_changed = True


def select_discharge_point_from_list(*args: Any) -> None:
    """Select a discharge point on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_discharge_point")
    app.map.layer[_MODEL].layer["discharge_points"].select_by_index(index)


def select_discharge_point_from_map(*args: Any) -> None:
    """Handle map-based selection of a discharge point.

    Parameters
    ----------
    *args : Any
        First element is a dict with an ``"id"`` key indicating the index.
    """
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_discharge_point", index)
    app.gui.window.update()
    _show_timeseries_popup(index)


def _show_timeseries_popup(index: int) -> None:
    """Generate a styled discharge timeseries popup for a clicked point.

    Parameters
    ----------
    index : int
        Index of the discharge point in the GeoDataFrame.
    """
    gdf = app.model[_MODEL].domain.discharge_points.gdf
    if gdf is None or index >= len(gdf):
        return

    data = app.model[_MODEL].domain.discharge_points.data
    if "dis" not in data:
        return

    ts = data.sel(index=index).to_dataframe().reset_index()
    ts = ts[["time", "dis"]].rename(columns={"dis": "discharge"})
    ts.set_index("time", inplace=True)

    if isinstance(ts, pd.DataFrame) and ts.empty:
        return

    name = gdf.iloc[index].get("name", f"Point {index}")
    geom = gdf.iloc[index].geometry
    map.show_timeseries_popup(
        ts,
        lon=geom.x,
        lat=geom.y,
        title=f"Discharge {name}",
        y_label="Discharge (m³/s)",
        html_name="discharge_point_time_series.html",
    )


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected discharge point.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_discharge_point")
    app.model[_MODEL].domain.discharge_points.delete(index)
    gdf = app.model[_MODEL].domain.discharge_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["discharge_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_discharge_point", index)
    app.model[_MODEL].discharge_points_changed = True
    update()
