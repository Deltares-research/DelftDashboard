"""GUI callbacks for the tropical cyclone draw track tab."""

from datetime import datetime, timedelta
from typing import Any

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from cht_cyclones import TropicalCyclone

from delftdashboard.app import app
from delftdashboard.operations import map

dateformat = "%Y%m%d %H%M%S"


def select(*args: Any) -> None:
    """Activate the draw tab."""
    map.update()
    app.toolbox["tropical_cyclone"].set_layer_mode("active")

    group = "tropical_cyclone"
    if app.gui.getvar(group, "draw_start_datetime") is None:
        app.gui.setvar(
            group,
            "draw_start_datetime",
            datetime.now().replace(minute=0, second=0, microsecond=0),
        )


def draw_track(*args: Any) -> None:
    """Start drawing a track polyline on the map with fixed-distance segments."""
    group = "tropical_cyclone"
    vt_knots = app.gui.getvar(group, "draw_vt")
    dt_hours = app.gui.getvar(group, "draw_dt_hours")

    # Distance per segment: vt (knots) * dt (hours) → nautical miles → km
    dst_nm = vt_knots * dt_hours
    dst_km = dst_nm * 1.852

    layer = app.map.layer["tropical_cyclone"].layer["draw_track"]
    layer.clear()
    layer.draw(fixed_distance=dst_km)


def track_drawn(gdf, feature_index, feature_id):
    """Called after the user finishes drawing the track polyline.

    Creates a new TropicalCyclone with a track built from the
    drawn polyline vertices.
    """
    group = "tropical_cyclone"
    toolbox = app.toolbox["tropical_cyclone"]

    geom = gdf.loc[feature_index, "geometry"]
    coords = list(geom.coords)

    if len(coords) < 2:
        return

    t0 = app.gui.getvar(group, "draw_start_datetime")
    dt_hours = app.gui.getvar(group, "draw_dt_hours")
    vmax = app.gui.getvar(group, "draw_vmax")
    rmax = app.gui.getvar(group, "draw_rmax")

    # Create a fresh TropicalCyclone
    # Build track GDF matching the cht_cyclones column schema
    # (ideally cht_cyclones would have a from_points() method for this)
    n = len(coords)
    track_gdf = gpd.GeoDataFrame(
        {
            "datetime": [(t0 + timedelta(hours=i * dt_hours)).strftime(dateformat) for i in range(n)],
            "geometry": [Point(lon, lat) for lon, lat in coords],
            "vmax": np.full(n, vmax),
            "pc": np.zeros(n),
            "RMW": np.full(n, rmax),
            "R35_NE": np.zeros(n),
            "R35_SE": np.zeros(n),
            "R35_SW": np.zeros(n),
            "R35_NW": np.zeros(n),
            "R50_NE": np.zeros(n),
            "R50_SE": np.zeros(n),
            "R50_SW": np.zeros(n),
            "R50_NW": np.zeros(n),
            "R65_NE": np.zeros(n),
            "R65_SE": np.zeros(n),
            "R65_SW": np.zeros(n),
            "R65_NW": np.zeros(n),
            "R100_NE": np.zeros(n),
            "R100_SE": np.zeros(n),
            "R100_SW": np.zeros(n),
            "R100_NW": np.zeros(n),
        },
        crs=4326,
    )

    name = app.gui.getvar(group, "draw_name")
    toolbox.tc = TropicalCyclone(name=name)
    toolbox.tc.track.gdf = track_gdf

    # Clear drawing layer and show as cyclone track
    app.map.layer["tropical_cyclone"].layer["draw_track"].clear()
    toolbox.track_added()



def save_track(*args: Any) -> None:
    """Save the current track to a .cyc file."""
    app.toolbox["tropical_cyclone"].save_track()
