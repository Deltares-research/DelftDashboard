"""GUI callbacks for the SFINCS HydroMT SnapWave Boundary Conditions sub-tab.

Handles adding, deleting, and editing SnapWave boundary points and their
parametric wave conditions (Hm0, Tp, direction, directional spreading),
as well as reading/writing .bnd, .bhs, and .nc files.
"""

import os
from typing import Any, Optional

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the SnapWave Boundary Conditions sub-tab and show points on map."""
    map.update()
    app.map.layer[_MODEL].layer["boundary_points_snapwave"].activate()
    update_list()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved wave boundary changes when leaving the tab."""
    if app.model[_MODEL].wave_boundaries_changed:
        ok = app.gui.window.dialog_yes_no(
            "The boundary conditions have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load SnapWave boundary points and time series from .bnd and .bhs/.nc files.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    # bnd file
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="snapwave.bnd",
        filter="*.bnd",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("snapwave_bndfile", rsp[2])
    else:
        # User pressed cancel
        return

    # Check if current time series file is netcdf or ascii, and set filter accordingly
    current_bhsfile = app.model[_MODEL].domain.config.get("snapwave_bhsfile")
    current_ncfile = app.model[_MODEL].domain.config.get("netsnapwavefile")

    if current_bhsfile:
        # ASCII
        current_file = current_bhsfile
    elif current_ncfile:
        # NetCDF
        current_file = current_ncfile
    else:
        # No current file, set default filter
        current_file = None

    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name=current_file,
        filter="*.bhs;*.nc",
        allow_directory_change=False,
    )
    if rsp[0]:
        # Determine if selected file is netcdf or ascii
        if rsp[2].endswith(".bhs"):
            # ASCII
            root, ext = os.path.splitext(rsp[2])
            app.model[_MODEL].domain.config.set("snapwave_bhsfile", rsp[2])
            app.model[_MODEL].domain.config.set("snapwave_btpfile", root + ".btp")
            app.model[_MODEL].domain.config.set("snapwave_bwdfile", root + ".bwd")
            app.model[_MODEL].domain.config.set("snapwave_bdsfile", root + ".bds")
            app.model[_MODEL].domain.config.set("netsnapwavefile", None)

        elif rsp[2].endswith(".nc"):
            # NetCDF
            app.model[_MODEL].domain.config.set("snapwave_bhsfile", None)
            app.model[_MODEL].domain.config.set("snapwave_btpfile", None)
            app.model[_MODEL].domain.config.set("snapwave_bwdfile", None)
            app.model[_MODEL].domain.config.set("snapwave_bdsfile", None)
            app.model[_MODEL].domain.config.set("netsnapwavefile", rsp[2])

        read_bhs_file = True

    else:
        # User pressed cancel. Do not read bzs file, but initialize boundary conditions anyway.
        read_bhs_file = False

    # Read boundary conditions
    app.model[_MODEL].domain.snapwave_boundary_conditions.read()

    if read_bhs_file:
        # Read boundary conditions from bzs file
        app.model[_MODEL].wave_boundaries_changed = False
    else:
        # Set uniform conditions
        set_uniform_conditions()
        app.model[_MODEL].wave_boundaries_changed = True

    # Add boundary points to map
    gdf = app.model[_MODEL].domain.snapwave_boundary_conditions.gdf
    app.map.layer[_MODEL].layer["boundary_points_snapwave"].set_data(gdf, 0)

    # Set active boundary point and update list
    app.gui.setvar(_GROUP, "active_boundary_point_snapwave", 0)
    update_list()


def save(*args: Any, **kwargs: Any) -> None:
    """Save SnapWave boundary points and time series to disk.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    **kwargs : Any
        Unused keyword arguments.
    """
    map.reset_cursor()

    # Save all files (bnd, bhs, btp, etc) related to boundary conditions

    bndfile = get_bnd_file_name()
    if bndfile is None:
        # User pressed cancel
        return

    bcfile = get_bhs_file_name()
    if bcfile is None:
        # User pressed cancel
        return

    # Write bnd files
    app.model[_MODEL].domain.snapwave_boundary_conditions.write_boundary_points()
    app.model[_MODEL].domain.config.set("snapwave_bndfile", bndfile)
    app.gui.setvar(_GROUP, "snapwave_bndfile", bndfile)

    # And now the time series

    # Get the file extension
    if bcfile.endswith(".bhs"):
        frmt = "ascii"
    elif bcfile.endswith(".nc"):
        frmt = "netcdf"
    else:
        app.gui.window.dialog_info(
            "Unsupported file format for time series file. Please select a .bhs or .nc file.",
            title="Error",
        )
        return

    # Get the root name of the time series file (without path and extension) to use for the other files
    bc_root = os.path.splitext(os.path.basename(bcfile))[0]

    if frmt == "ascii":
        app.model[_MODEL].domain.config.set("snapwave_bhsfile", bc_root + ".bhs")
        app.model[_MODEL].domain.config.set("snapwave_btpfile", bc_root + ".btp")
        app.model[_MODEL].domain.config.set("snapwave_bwdfile", bc_root + ".bwd")
        app.model[_MODEL].domain.config.set("snapwave_bdsfile", bc_root + ".bds")

        app.model[_MODEL].domain.config.set("netsnapwavefile", None)

        app.model[
            _MODEL
        ].domain.snapwave_boundary_conditions.write_boundary_conditions_timeseries_all()

    else:
        app.model[
            _MODEL
        ].domain.snapwave_boundary_conditions.write_boundary_conditions_netcdf()

        app.model[_MODEL].domain.config.set("netsnapwavefile", bcfile)

        app.model[_MODEL].domain.config.set("snapwave_bhsfile", None)
        app.model[_MODEL].domain.config.set("snapwave_btpfile", None)
        app.model[_MODEL].domain.config.set("snapwave_bwdfile", None)
        app.model[_MODEL].domain.config.set("snapwave_bdsfile", None)

    app.model[_MODEL].wave_boundaries_changed = False


def add_boundary_point_on_map_snapwave(*args: Any) -> None:
    """Start map click interaction to add a new SnapWave boundary point."""
    app.map.click_point(point_clicked)


def point_clicked(x: float, y: float) -> None:
    """Handle a map click to add a SnapWave boundary point at *(x, y)*.

    Parameters
    ----------
    x : float
        Longitude or x-coordinate of the clicked location.
    y : float
        Latitude or y-coordinate of the clicked location.
    """
    app.model[_MODEL].domain.snapwave_boundary_conditions.add_point(x, y)
    index = len(app.model[_MODEL].domain.snapwave_boundary_conditions.gdf) - 1
    set_uniform_conditions(index=index)
    gdf = app.model[_MODEL].domain.snapwave_boundary_conditions.gdf
    app.map.layer[_MODEL].layer["boundary_points_snapwave"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_boundary_point_snapwave", index)
    update_list()
    app.model[_MODEL].wave_boundaries_changed = True


def select_boundary_point_from_list_snapwave(*args: Any) -> None:
    """Select a SnapWave boundary point on the map from the GUI list.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "active_boundary_point_snapwave")
    app.map.layer[_MODEL].layer["boundary_points_snapwave"].select_by_index(index)


def select_boundary_point_from_map_snapwave(*args: Any) -> None:
    """Handle map-based selection of a SnapWave boundary point.

    Parameters
    ----------
    *args : Any
        First element is a dict with an ``"id"`` key indicating the index.
    """
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_boundary_point_snapwave", index)
    app.gui.window.update()


def delete_point_from_list_snapwave(*args: Any) -> None:
    """Delete the currently selected SnapWave boundary point.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "active_boundary_point_snapwave")
    app.model[_MODEL].domain.snapwave_boundary_conditions.delete(index)
    gdf = app.model[_MODEL].domain.snapwave_boundary_conditions.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["boundary_points_snapwave"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_boundary_point_snapwave", index)
    update_list()
    app.model[_MODEL].wave_boundaries_changed = True


def update_list() -> None:
    """Refresh the SnapWave boundary point name list and count in the GUI."""
    nr_boundary_points = app.model[_MODEL].domain.snapwave_boundary_conditions.nr_points
    boundary_point_names = app.model[
        _MODEL
    ].domain.snapwave_boundary_conditions.list_names
    app.gui.setvar(_GROUP, "boundary_point_names_snapwave", boundary_point_names)
    app.gui.setvar(_GROUP, "nr_boundary_points_snapwave", nr_boundary_points)
    app.gui.window.update()


def set_boundary_conditions_snapwave(*args: Any) -> None:
    """Apply uniform wave conditions to all SnapWave boundary points from the GUI."""
    set_uniform_conditions()
    app.model[_MODEL].wave_boundaries_changed = True


def set_uniform_conditions(index: Optional[int] = None) -> None:
    """Apply uniform wave conditions from GUI values to boundary points.

    Parameters
    ----------
    index : int or None
        Index of a specific point to update. If ``None``, update all points.
    """
    hm0 = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_hm0_snapwave")
    tp = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_tp_snapwave")
    wd = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_wd_snapwave")
    ds = app.gui.getvar(_GROUP, "boundary_conditions_timeseries_ds_snapwave")
    app.model[_MODEL].domain.snapwave_boundary_conditions.set_uniform_conditions(
        hm0, tp, wd, ds, index=index
    )


def view_boundary_conditions_snapwave(*args: Any) -> None:
    """Display SnapWave boundary conditions (not yet implemented)."""
    print("Viewing boundary conditions not implemented yet")


def create_boundary_points_snapwave(*args: Any) -> None:
    """Generate SnapWave boundary points from the SnapWave mask open boundaries.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    # First check if there are already boundary points
    if app.model[_MODEL].domain.snapwave_boundary_conditions.nr_points > 0:
        ok = app.gui.window.dialog_ok_cancel(
            "Existing boundary points will be overwritten! Continue?", title="Warning"
        )
        if not ok:
            return
    # Check for open boundary points in mask
    mask = app.model[_MODEL].domain.quadtree_grid.data["snapwave_mask"]
    if mask is None:
        ok = app.gui.window.dialog_info(
            "Please first create a mask for this domain.", title=" "
        )
        return
    if not app.model[_MODEL].domain.quadtree_snapwave_mask.has_open_boundaries:
        ok = app.gui.window.dialog_info(
            "The mask for this domain does not have any open boundary points !",
            title=" ",
        )
        return

    bndfile = get_bnd_file_name()
    if bndfile is None:
        return

    # Create points from mask
    bnd_dist = app.gui.getvar(_GROUP, "boundary_dx_snapwave")
    # Use old "cht_sfincs" method for now.
    app.model[
        _MODEL
    ].domain.snapwave_boundary_conditions.create_boundary_points_from_mask(
        bnd_dist=bnd_dist
    )
    gdf = app.model[_MODEL].domain.snapwave_boundary_conditions.gdf
    if app.model[_MODEL].domain.snapwave_boundary_conditions.nr_points == 0:
        app.gui.window.dialog_info(
            "No boundary points found in mask. Please check mask settings.",
            title="Warning",
        )
        return

    app.map.layer[_MODEL].layer["boundary_points_snapwave"].set_data(gdf, 0)

    # Set uniform conditions
    set_boundary_conditions_snapwave()

    # And save everything
    save()

    app.gui.setvar(_GROUP, "active_boundary_point_snapwave", 0)
    update_list()


def get_bnd_file_name(*args: Any) -> Optional[str]:
    """Prompt the user to select or confirm a SnapWave .bnd file name.

    Returns
    -------
    str or None
        The selected file name, or ``None`` if the user cancelled.
    """
    filename = app.model[_MODEL].domain.config.get("snapwave_bndfile")
    if not filename:
        filename = "snapwave.bnd"
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


def get_bhs_file_name(*args: Any) -> Optional[str]:
    """Prompt the user to select or confirm a SnapWave time series file name.

    Returns
    -------
    str or None
        The selected file name, or ``None`` if the user cancelled.
    """
    filename = app.model[_MODEL].domain.config.get("snapwave_bhsfile")
    if not filename:
        filename = "snapwave.bhs"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.bhs;*.nc",
        allow_directory_change=False,
    )
    if rsp[0]:
        return rsp[2]
    else:
        # User pressed cancel
        return None
