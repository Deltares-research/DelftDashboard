"""GUI callbacks for the SFINCS HydroMT Timeframe tab.

Handles tab selection, model variable synchronization, and time
consistency checks for simulation start/stop times and output intervals.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Timeframe tab and update map layers.

    Also deactivates existing map layers and sets up the commented-out
    observation-point demo layer.
    """
    # from geopandas import GeoDataFrame
    # from shapely.geometry import Point
    # gdf = GeoDataFrame(geometry=[Point(0, 0)], crs=4326)
    # # Add a url property to the geodataframe
    # url_list = ["https://www.google.com"]
    # des_list = ["Description"]
    # gdf["url"] = url_list
    # gdf["description"] = des_list
    # gdf["icon_url"] = "tide_icon_48x48.png"
    # app.map.layer["sfincs_hmt"].layer["obs_points"].set_data(gdf)

    map.update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config and check times."""
    app.model[_MODEL].set_model_variables()

    # Now check that the boundary and other forcing fully covers the simulation time
    app.model[_MODEL].check_times()
