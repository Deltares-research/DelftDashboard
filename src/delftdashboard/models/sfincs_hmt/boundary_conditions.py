"""GUI callbacks for the SFINCS HydroMT Boundary Conditions tab.

Handles adding, deleting, and editing water-level boundary points,
generating tidal boundary conditions, and reading/writing .bnd, .bzs,
and .bca files.
"""

import os
from typing import Any, Optional

import pandas as pd
import plotly.express as px

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Boundary Conditions tab and show boundary points on map."""
    map.update()
    app.map.layer[_MODEL].layer["boundary_points"].activate()
    update_list()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved boundary changes when leaving the tab."""
    if app.model[_MODEL].boundaries_changed:
        ok = app.gui.window.dialog_yes_no(
            "The boundary conditions have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load boundary points and time series from .bnd and .bzs files.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    # bnd file
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.bnd",
        filter="*.bnd",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("bndfile", rsp[2])
    else:
        # User pressed cancel
        return
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.bzs",
        filter="*.bzs",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("bzsfile", rsp[2])
        read_bzs_file = True
    else:
        # User pressed cancel. Do not read bzs file, but initialize boundary conditions anyway.
        read_bzs_file = False

    # Read boundary points from bnd file
    app.model[_MODEL].domain.water_level.read()

    if read_bzs_file:
        # Read boundary conditions from bzs file
        app.model[_MODEL].domain.water_level.read_boundary_conditions_timeseries()
    else:
        # Set uniform conditions
        set_boundary_conditions()

    # Add boundary points to map
    gdf = app.model[_MODEL].domain.water_level.gdf
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, 0)

    # Set active boundary point and update list
    app.gui.setvar(_GROUP, "active_boundary_point", 0)
    update_list()
    app.model[_MODEL].boundaries_changed = False


def save(*args: Any, **kwargs: Any) -> None:
    """Save boundary points and time series to .bnd and .bzs files.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    **kwargs : Any
        Unused keyword arguments.
    """
    map.reset_cursor()

    # Save both bnd and bzs files (not the bca file for now)

    bndfile = get_bnd_file_name()
    bzsfile = get_bzs_file_name()

    if bndfile is None or bzsfile is None:
        return

    app.model[_MODEL].domain.config.set("bndfile", bndfile)
    app.model[_MODEL].domain.config.set("bzsfile", bzsfile)
    app.gui.setvar(_GROUP, "bndfile", bndfile)
    app.gui.setvar(_GROUP, "bzsfile", bzsfile)

    # Bca is already saved when generating boundary conditions from tide model.
    # However, if points were added or removed, the astro components should be generated again. But we're not doing that now. Maybe later.
    if app.model[_MODEL].domain.config.get("bcafile") is not None:
        astro_okay = True
        for index, row in app.model[_MODEL].domain.water_level.gdf.iterrows():
            if len(row["astro"]) == 0:
                astro_okay = False
                break
        if not astro_okay:
            # Give warning
            app.gui.window.dialog_info(
                "Astronomical constituents are missing in some points. You'll need to generate them again to avoid possible errors.",
                title="Warning",
            )

    # Write bnd and bzs files
    app.model[_MODEL].domain.water_level.write()
    app.model[_MODEL].domain.water_level.write_boundary_conditions_timeseries()
    app.model[_MODEL].boundaries_changed = False


def add_boundary_point_on_map(*args: Any) -> None:
    """Start map click interaction to add a new boundary point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a boundary point at *(x, y)*.

    Parameters
    ----------
    x : float
        Longitude or x-coordinate of the clicked location.
    y : float
        Latitude or y-coordinate of the clicked location.
    """
    wl = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_offset")
    app.model[_MODEL].domain.water_level.add_point(x, y, value=wl)
    index = app.model[_MODEL].domain.water_level.nr_points - 1
    gdf = app.model[_MODEL].domain.water_level.gdf
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    update_list()
    app.model[_MODEL].boundaries_changed = True


def select_boundary_point_from_list(*args: Any) -> None:
    """Select a boundary point on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        First argument is the selected index value from the listbox.
    """
    # Use the index passed directly from the listbox callback,
    # not from getvar (which may be stale due to async JS updates)
    if args:
        index = args[0]
        if isinstance(index, tuple):
            index = index[0]
        index = int(index)
    else:
        index = app.gui.getvar(_GROUP, "active_boundary_point")
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    app.map.layer[_MODEL].layer["boundary_points"].select_by_index(index)


def select_boundary_point_from_map(*args: Any) -> None:
    """Handle map-based selection of a boundary point.

    Opens a plotly time series popup for the selected point.

    Parameters
    ----------
    *args : Any
        First element is a dict with an ``"id"`` key indicating the index.
    """
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    app.gui.window.update()
    _show_timeseries_popup(index)


def delete_point_from_list(*args: Any) -> None:
    """Delete the currently selected boundary point.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    app.model[_MODEL].domain.water_level.delete(index)
    gdf = app.model[_MODEL].domain.water_level.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    update_list()
    app.model[_MODEL].boundaries_changed = True


def select_timeseries_or_astro(*args: Any) -> None:
    """Handle toggling between timeseries and astronomical boundary types."""
    app.gui.window.update()


def update_list() -> None:
    """Refresh the boundary point name list and count in the GUI."""
    nr_boundary_points = app.model[_MODEL].domain.water_level.nr_points
    boundary_point_names = []
    # Loop through boundary points
    for index, row in app.model[_MODEL].domain.water_level.gdf.iterrows():
        name = f"Point {index + 1:03d}"
        boundary_point_names.append(name)
    app.gui.setvar(_GROUP, "boundary_point_names", boundary_point_names)
    app.gui.setvar(_GROUP, "nr_boundary_points", nr_boundary_points)
    app.gui.window.update()


def generate_boundary_conditions_from_tide_model(*args: Any) -> None:
    """Generate astronomical boundary conditions from the selected tide model.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()

    # Ask for name of bca file
    bcafile = get_bca_file_name()

    if bcafile is None:
        return

    app.model[_MODEL].domain.config.set("bcafile", bcafile)
    app.gui.setvar(_GROUP, "bcafile", bcafile)

    # Now interpolate tidal data to boundary points
    tide_model_name = app.gui.getvar(_GROUP, "boundary_conditions_tide_model")
    gdf = app.model[_MODEL].domain.water_level.gdf
    tide_model = app.tide_model_database.get_dataset(tide_model_name)
    gdf = tide_model.get_data_on_points(
        gdf=gdf, crs=app.model[_MODEL].domain.crs, format="gdf", constituents="all"
    )
    # TODO: Following still needs to be built into HydroMT-SFINCS
    app.model[_MODEL].domain.water_level.from_gdf(gdf)

    # Save bca file
    app.model[_MODEL].domain.water_level.write_boundary_conditions_astro()
    app.gui.setvar(_GROUP, "boundary_conditions_timeseries_shape", "astronomical")

    set_boundary_conditions()  # This is where the bzs file gets saved

    app.gui.window.update()


def set_boundary_conditions(*args: Any) -> None:
    """Generate and write boundary condition time series from GUI parameters.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    bzsfile = get_bzs_file_name()
    if bzsfile is None:
        return

    app.model[_MODEL].domain.config.set("bzsfile", bzsfile)
    app.gui.setvar(_GROUP, "bzsfile", bzsfile)

    dlg = app.gui.window.dialog_wait("Generating boundary conditions ...")

    shape = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_shape")
    timestep = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_time_step")
    offset = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_offset")
    amplitude = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_amplitude")
    phase = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_phase")
    period = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_period")
    peak = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_peak")
    tpeak = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_tpeak")
    duration = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_duration")

    app.model[_MODEL].domain.water_level.create_timeseries(
        shape=shape,
        timestep=timestep,
        offset=offset,
        amplitude=amplitude,
        phase=phase,
        period=period,
        peak=peak,
        tpeak=tpeak,
        duration=duration,
    )
    dlg.close()

    # Save the bzs file
    app.model[_MODEL].domain.water_level.write_boundary_conditions_timeseries()
    app.model[_MODEL].boundaries_changed = False


def view_boundary_conditions(*args: Any) -> None:
    """Display boundary conditions (not yet implemented)."""
    print("Viewing boundary conditions not implemented yet")


def create_boundary_points(*args: Any) -> None:
    """Generate boundary points from the grid mask open boundaries.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    # First check if there are already boundary points
    if app.model[_MODEL].domain.water_level.nr_points > 0:
        ok = app.gui.window.dialog_ok_cancel(
            "Existing boundary points will be overwritten! Continue?", title="Warning"
        )
        if not ok:
            return
    # Check for open boundary points in mask
    mask = app.model[_MODEL].domain.quadtree_grid.data["mask"]
    if mask is None:
        ok = app.gui.window.dialog_info(
            "Please first create a mask for this domain.", title=" "
        )
        return
    if not app.model[_MODEL].domain.quadtree_mask.has_open_boundaries:
        ok = app.gui.window.dialog_info(
            "The mask for this domain does not have any open boundary points !",
            title=" ",
        )
        return

    bndfile = get_bnd_file_name()
    if bndfile is None:
        return

    # Create points from mask
    bnd_dist = app.gui.getvar(_GROUP, "boundary_dx")
    app.model[_MODEL].domain.water_level.create_boundary_points_from_mask(
        bnd_dist=bnd_dist
    )
    gdf = app.model[_MODEL].domain.water_level.gdf
    if len(gdf) == 0:
        app.gui.window.dialog_info(
            "No boundary points found in mask. Please check mask settings.",
            title="Warning",
        )
        return

    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, 0)
    # Set uniform conditions
    app.gui.setvar(_GROUP, "boundary_conditions_timeseries_shape", "constant")

    # Write bnd file
    app.model[_MODEL].domain.config.set("bndfile", bndfile)
    app.gui.setvar(_GROUP, "bndfile", bndfile)
    app.model[_MODEL].domain.water_level.write_boundary_points()

    set_boundary_conditions()

    app.gui.setvar(_GROUP, "active_boundary_point", 0)
    update_list()


def _show_timeseries_popup(index: int) -> None:
    """Generate a plotly time series plot and show it as a map popup.

    Parameters
    ----------
    index : int
        Index of the boundary point in the GeoDataFrame.
    """

    gdf = app.model[_MODEL].domain.water_level.gdf
    if gdf is None or index >= len(gdf):
        return

    # The time series are stored in app.model[_MODEL].domain.water_level.data as an xr.Dataset,
    # but we need to get the time series for this point as a pandas DataFrame for plotting.
    # We can get the point ID from the gdf, and then use that to select the time series from the Dataset.
    # We need the time series for our point with index `index` as a pandas DataFrame with columns "time" and "value".
    # The time series are stored in app.model[_MODEL].domain.water_level.data as an xarray Dataset,
    # where each point has a unique ID that matches the "id" column in the gdf.
    # We can use the point ID to select the time series for this point from the Dataset,
    # and then convert it to a pandas DataFrame for plotting.
    ts = app.model[_MODEL].domain.water_level.data.sel(index=index).to_dataframe().reset_index()
    # And we only need the bzs column
    ts = ts[["time", "bzs"]].rename(columns={"bzs": "water_level"})
    ts.set_index("time", inplace=True)

    if ts is None or (isinstance(ts, pd.DataFrame) and ts.empty):
        return

    name = gdf.iloc[index].get("name", f"Point {index}")

    # Build the plotly figure
    fig = px.line(
        ts,
        title=f"Boundary: {name}",
        labels={"time": "Time", "water_level": "Water Level (m)"},
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=40, b=30),
        height=300,
        width=500,
        template="plotly_white",
        showlegend=False,
        yaxis_title="Water Level (m)",
        xaxis_title="Time",
    )

    # Save as HTML in the server overlays folder
    html_file = "boundary_point_time_series.html"
    html_path = os.path.join(app.map.server_path, "overlays", html_file)
    fig.write_html(
        html_path,
        include_plotlyjs="cdn",
        full_html=True,
        config={"displayModeBar": False},
    )

    # Show as popup on the map at the boundary point location
    geom = gdf.iloc[index].geometry
    lon, lat = geom.x, geom.y
    url = f"./overlays/{html_file}"
    app.map.runjs(
        "/js/main.js", "showPopup",
        lon=lon, lat=lat, url=url, width=520, height=320,
    )

def get_bnd_file_name(*args: Any) -> Optional[str]:
    """Prompt the user to select or confirm a .bnd file name.

    Returns
    -------
    str or None
        The selected file name, or ``None`` if the user cancelled.
    """
    filename = app.model[_MODEL].domain.config.get("bndfile")
    if not filename:
        filename = "sfincs.bnd"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bnd",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None


def get_bzs_file_name(*args: Any) -> Optional[str]:
    """Prompt the user to select or confirm a .bzs file name.

    Returns
    -------
    str or None
        The selected file name, or ``None`` if the user cancelled.
    """
    filename = app.model[_MODEL].domain.config.get("bzsfile")
    if not filename:
        filename = "sfincs.bzs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bzs",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None


def get_bca_file_name(*args: Any) -> Optional[str]:
    """Prompt the user to select or confirm a .bca file name.

    Returns
    -------
    str or None
        The selected file name, or ``None`` if the user cancelled.
    """
    filename = app.model[_MODEL].domain.config.get("bcafile")
    if not filename:
        filename = "sfincs.bca"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bca",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None
