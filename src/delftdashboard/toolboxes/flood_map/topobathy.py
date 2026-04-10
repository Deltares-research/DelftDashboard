"""GUI callbacks for the flood map topobathy tab.

Handle polygon drawing for custom extents and topobathy GeoTIFF generation.
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the topobathy tab and enable polygon drawing."""
    map.update()
    app.toolbox["flood_map"].set_layer_mode("active")
    app.map.layer["flood_map"].layer["polygon"].show()
    app.map.layer["flood_map"].layer["polygon"].activate()


def generate_topobathy_geotiff(*args: Any) -> None:
    """Generate a topobathy GeoTIFF for the current extent."""
    app.toolbox["flood_map"].generate_topobathy_geotiff()


def draw_polygon(*args: Any) -> None:
    """Start drawing a new polygon after clearing existing ones."""
    delete_polygon()
    app.map.layer["flood_map"].layer["polygon"].crs = app.crs
    app.map.layer["flood_map"].layer["polygon"].draw()


def delete_polygon(*args: Any) -> None:
    """Delete the current polygon from the map and toolbox state."""
    app.toolbox["flood_map"].polygon = gpd.GeoDataFrame()
    app.map.layer["flood_map"].layer["polygon"].clear()


def polygon_created(gdf: gpd.GeoDataFrame, index: int, id: Any) -> None:
    """Store a newly created polygon.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing the polygon geometries.
    index : int
        Index of the created feature.
    id : Any
        Identifier of the created feature.
    """
    app.toolbox["flood_map"].polygon = gdf
