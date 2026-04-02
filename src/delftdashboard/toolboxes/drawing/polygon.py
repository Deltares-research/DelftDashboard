"""GUI callbacks for the drawing polygon tab.

Handle polygon drawing, selection, loading, saving, buffering, and merging.
"""

from typing import Any

import geopandas as gpd
import pandas as pd
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the polygon tab and show polygon layers."""
    map.update()
    app.map.layer["drawing"].show()
    app.map.layer["drawing"].layer["polygon"].show()
    app.map.layer["drawing"].layer["polygon"].activate()
    app.map.layer["drawing"].layer["polygon_tmp"].show()
    update()


def draw_polygon(*args: Any) -> None:
    """Start drawing a new polygon on the map."""
    layer = app.map.layer["drawing"].layer["polygon"]
    layer.draw()


def select_polygon(*args: Any) -> None:
    """Activate the polygon selected from the list on the map."""
    iac = app.gui.getvar("drawing", "active_polygon")
    app.map.layer["drawing"].layer["polygon"].activate_feature(iac)


def delete_polygon(*args: Any) -> None:
    """Delete the currently active polygon."""
    iac = app.gui.getvar("drawing", "active_polygon")
    app.toolbox["drawing"].polygon = (
        app.toolbox["drawing"].polygon.drop(index=iac).reset_index(drop=True)
    )
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()


def load_polygon(*args: Any) -> None:
    """Load polygons from a GeoJSON file."""
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        filter="*.geojson",
        allow_directory_change=True,
    )
    if rsp[0]:
        if app.gui.getvar("drawing", "nr_polygons") > 0:
            append = app.gui.window.dialog_yes_no("Add to existing polygons?", " ")
        else:
            append = False
        app.toolbox["drawing"].polygon_file_name = rsp[0]
        gdf = gpd.read_file(app.toolbox["drawing"].polygon_file_name)
        gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No polygons found in file", "Error")
            return
        if append:
            gdf = gdf.to_crs(app.toolbox["drawing"].polygon.crs)
            app.toolbox["drawing"].polygon = pd.concat(
                [app.toolbox["drawing"].polygon, gdf]
            )
        else:
            app.toolbox["drawing"].polygon = gdf
        app.map.layer["drawing"].layer["polygon"].set_data(
            app.toolbox["drawing"].polygon
        )
        update()


def save_polygon(*args: Any) -> None:
    """Save polygons to a GeoJSON file."""
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=app.toolbox["drawing"].polygon_file_name,
        filter="*.geojson",
        allow_directory_change=True,
    )
    if rsp[0]:
        app.toolbox["drawing"].polygon_file_name = rsp[0]
        gdf = gpd.GeoDataFrame(
            geometry=app.toolbox["drawing"].polygon.geometry
        ).set_crs(app.toolbox["drawing"].polygon.crs)
        gdf.to_file(app.toolbox["drawing"].polygon_file_name, driver="GeoJSON")


def polygon_created(gdf: gpd.GeoDataFrame, feature_index: int, feature_id: Any) -> None:
    """Store a newly created polygon from the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all polygon geometries.
    feature_index : int
        Index of the newly created feature.
    feature_id : Any
        Identifier of the newly created feature.
    """
    app.toolbox["drawing"].polygon = gdf
    app.gui.setvar("drawing", "active_polygon", feature_index)
    update()


def polygon_modified(gdf: gpd.GeoDataFrame, index: int, feature_id: Any) -> None:
    """Update state after a polygon is modified on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing all polygon geometries.
    index : int
        Index of the modified feature.
    feature_id : Any
        Identifier of the modified feature.
    """
    app.toolbox["drawing"].polygon = gdf
    app.gui.setvar("drawing", "active_polygon", index)
    update()


def polygon_selected(index: int) -> None:
    """Handle polygon selection on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar("drawing", "active_polygon", index)
    update()


def edit_polygon_buffer_distance(*args: Any) -> None:
    """Update the temporary buffer layer after distance change."""
    update_temp_layer()


def apply_buffer(*args: Any) -> None:
    """Apply the buffer distance to all polygons permanently."""
    gdf = get_buffered_polygons()
    app.toolbox["drawing"].polygon = gdf
    app.map.layer["drawing"].layer["polygon"].set_data(gdf)
    app.gui.setvar("drawing", "polygon_buffer_distance", 0.0)
    update()


def merge_polygons(*args: Any) -> None:
    """Merge all polygons into a single geometry."""
    geom = app.toolbox["drawing"].polygon.unary_union
    if geom.geom_type == "Polygon":
        geom_list = [geom]
    else:
        geom_list = list(geom.geoms)
    app.toolbox["drawing"].polygon = gpd.GeoDataFrame(geometry=geom_list).set_crs(
        app.toolbox["drawing"].polygon.crs
    )
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()


def update() -> None:
    """Refresh polygon list, names, and temporary layers."""
    npol = len(app.toolbox["drawing"].polygon)
    app.gui.setvar("drawing", "nr_polygons", npol)
    iac = app.gui.getvar("drawing", "active_polygon")
    iac = max(min(iac, npol - 1), 0)
    app.gui.setvar("drawing", "active_polygon", iac)

    update_polygon_names()
    update_temp_layer()

    app.gui.window.update()


def update_polygon_names() -> None:
    """Rebuild the polygon name list for the GUI."""
    names = []
    for i in range(len(app.toolbox["drawing"].polygon)):
        names.append(f"polygon_{i + 1}")
    app.gui.setvar("drawing", "polygon_names", names)


def update_temp_layer() -> None:
    """Update the temporary buffer preview layer."""
    layer = app.map.layer["drawing"].layer["polygon_tmp"]
    layer.clear()
    if len(app.toolbox["drawing"].polygon) > 0:
        buffer_distance = app.gui.getvar("drawing", "polygon_buffer_distance")
        if buffer_distance > 0.0:
            gdf = get_buffered_polygons()
            layer.set_data(gdf)


def get_buffered_polygons() -> gpd.GeoDataFrame:
    """Compute buffered versions of all polygons.

    Returns
    -------
    gpd.GeoDataFrame
        Buffered polygon geometries.
    """
    buffer_distance = app.gui.getvar("drawing", "polygon_buffer_distance")
    if app.toolbox["drawing"].polygon.crs.is_geographic:
        lon = app.toolbox["drawing"].polygon.centroid.x.mean()
        lat = app.toolbox["drawing"].polygon.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
        )
        geom = app.toolbox["drawing"].polygon.to_crs(aeqd_proj).buffer(buffer_distance)
        gdf = (
            gpd.GeoDataFrame(geom, columns=["geometry"])
            .set_crs(aeqd_proj)
            .to_crs(app.toolbox["drawing"].polygon.crs)
        )
    else:
        geom = app.toolbox["drawing"].polygon.buffer(buffer_distance)
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).to_crs(
            app.toolbox["drawing"].polygon.crs
        )

    return gdf
