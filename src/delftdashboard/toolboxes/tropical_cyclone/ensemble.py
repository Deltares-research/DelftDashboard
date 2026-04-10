"""GUI callbacks for the tropical cyclone ensemble tab.

Handle ensemble generation, cone plotting, and track time selection.
"""

from datetime import datetime
from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the ensemble tab and show ensemble layers."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble"].show()
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble_cone"].show()
    update_track_time_strings()


def make_ensemble(*args: Any) -> None:
    """Generate an ensemble of tropical cyclone tracks."""
    tc = app.toolbox["tropical_cyclone"].tc
    tstart = app.gui.getvar("tropical_cyclone", "ensemble_start_time")
    duration = app.gui.getvar("tropical_cyclone", "ensemble_duration")
    nr_realizations = app.gui.getvar(
        "tropical_cyclone", "ensemble_number_of_realizations"
    )
    p = app.gui.window.dialog_wait(
        "               Generating ensemble ...                "
    )
    ensemble = tc.make_ensemble(
        duration=duration,
        tstart=tstart,
        compute_wind_fields=False,
        number_of_realizations=nr_realizations,
    )
    p.close()
    app.toolbox["tropical_cyclone"].ensemble = ensemble
    plot_ensemble_tracks()
    plot_ensemble_cone()


def edit_cone_buffer(*args: Any) -> None:
    """Replot the ensemble cone after editing the buffer distance."""
    plot_ensemble_cone()


def edit_duration(*args: Any) -> None:
    """Handle ensemble duration edit events (placeholder)."""


def edit_number_of_realizations(*args: Any) -> None:
    """Handle ensemble realization count edit events (placeholder)."""


def select_tstart(*args: Any) -> None:
    """Set the ensemble start time from the selected track time."""
    index = app.gui.getvar("tropical_cyclone", "ensemble_start_time_index")
    track_time_strings = app.gui.getvar("tropical_cyclone", "track_time_strings")
    if len(track_time_strings) > 0:
        tstart = datetime.strptime(track_time_strings[index], "%Y%m%d %H%M%S")
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", tstart)
    else:
        app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)


def plot_ensemble_tracks() -> None:
    """Plot the ensemble track lines on the map."""
    gdf = (
        app.toolbox["tropical_cyclone"]
        .ensemble.to_gdf(option="tracks", filename=None)
        .set_crs(epsg=4326)
    )
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble"].set_data(gdf)


def plot_ensemble_cone() -> None:
    """Plot the ensemble uncertainty cone on the map."""
    cone_buffer = app.gui.getvar("tropical_cyclone", "ensemble_cone_buffer")
    only_forecast = app.gui.getvar("tropical_cyclone", "ensemble_cone_only_forecast")
    gdf_cone = (
        app.toolbox["tropical_cyclone"]
        .ensemble.to_gdf(
            option="cone",
            filename=None,
            buffer=cone_buffer,
            only_forecast=only_forecast,
        )
        .set_crs(epsg=4326)
    )
    app.map.layer["tropical_cyclone"].layer["cyclone_track_ensemble_cone"].set_data(
        gdf_cone
    )


def update_track_time_strings() -> None:
    """Update the list of track time strings from the loaded cyclone track."""
    track_time_strings = []
    if app.toolbox["tropical_cyclone"].tc is None:
        return
    for i in range(len(app.toolbox["tropical_cyclone"].tc.track.gdf)):
        track_time_strings.append(
            app.toolbox["tropical_cyclone"].tc.track.gdf.loc[i, "datetime"]
        )
    app.gui.setvar("tropical_cyclone", "track_time_strings", track_time_strings)
