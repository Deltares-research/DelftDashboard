"""GUI callbacks for Delft3D-FM boundary condition management."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate boundary and grid layers when the boundary tab is selected."""
    map.update()
    app.map.layer[_MODEL].layer["boundary_line"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()


def deselect(*args: Any) -> None:
    """Prompt the user to save unsaved boundary changes on tab deselect."""
    if app.model[_MODEL].boundaries_changed:
        ok = app.gui.window.dialog_yes_no(
            "The boundary conditions have changed. Would you like to save the changes?"
        )
        if ok:
            save()
        else:
            app.model[_MODEL].boundaries_changed = False


def generate_boundary_conditions_from_tide_model(*args: Any) -> None:
    """Interpolate tidal constituents onto boundary points and write forcing files."""
    tide_model_name = app.gui.getvar(_MODEL, "boundary_conditions_tide_model")
    gdf = app.model[_MODEL].domain.boundary_conditions.gdf_points
    tide_model = app.tide_model_database.get_dataset(tide_model_name)
    gdf_points = tide_model.get_data_on_points(
        gdf=gdf, crs=app.model[_MODEL].domain.crs, format="gdf", constituents="all"
    )
    app.model[_MODEL].domain.boundary_conditions.gdf_points = tide_model.add_offset(
        gdf_points, offset=app.gui.getvar(_MODEL, "boundary_conditions_tide_offset")
    )

    # Save water level forcing file
    app.model[_MODEL].domain.boundary_conditions.write_boundary_conditions_astro()

    # Now save the external forcing file
    app.model[_MODEL].domain.boundary_conditions.write_ext_wl()


def generate_boundary_conditions_custom(*args: Any) -> None:
    """Generate custom boundary condition timeseries from GUI parameters."""
    dlg = app.gui.window.dialog_wait("Generating boundary conditions ...")

    shape = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_shape")
    timestep = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_time_step")
    offset = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_offset")
    amplitude = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_amplitude")
    phase = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_phase")
    period = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_period")
    peak = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_peak")
    tpeak = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_tpeak")
    duration = app.gui.getvar(_MODEL, "boundary_conditions_timeseries_duration")
    app.model[_MODEL].domain.boundary_conditions.set_timeseries(
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

    # Save water level forcing file
    app.model[_MODEL].domain.boundary_conditions.write_boundary_conditions_timeseries()

    # Now save the external forcing file
    app.model[_MODEL].domain.boundary_conditions.write_ext_wl(forcingtype="bzs")


def set_model_variables(*args: Any) -> None:
    """Copy all GUI variable values into the domain input object."""
    app.model[_MODEL].set_input_variables()
