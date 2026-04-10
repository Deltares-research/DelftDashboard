"""GUI callbacks and helper functions for polyline drawing, buffering, and offset operations."""

from __future__ import annotations

import warnings
from typing import Any

import geopandas as gpd
import pandas as pd
from pyproj import CRS
from shapely.ops import unary_union

from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks


def select(*args: Any) -> None:
    """Activate the polyline tab and show related map layers.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.update()
    app.map.layer["drawing"].show()
    app.map.layer["drawing"].layer["polyline"].activate()
    app.map.layer["drawing"].layer["polyline_tmp"].show()
    app.map.layer["drawing"].layer["polyline_asym_tmp"].show()
    app.map.layer["drawing"].layer["polyline_parallel_offset_tmp"].show()

    warnings.filterwarnings("ignore", message="Geometry is in a geographic CRS")


def draw_polyline(*args: Any) -> None:
    """Start interactive polyline drawing on the map.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    layer = app.map.layer["drawing"].layer["polyline"]
    layer.draw()


def select_polyline(*args: Any) -> None:
    """Activate the polyline selected from the list on the map.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    iac = app.gui.getvar("drawing", "active_polyline")
    app.map.layer["drawing"].layer["polyline"].activate_feature(iac)


def delete_polyline(*args: Any) -> None:
    """Delete the currently active polyline.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    iac = app.gui.getvar("drawing", "active_polyline")
    app.toolbox["drawing"].polyline = (
        app.toolbox["drawing"].polyline.drop(index=iac).reset_index(drop=True)
    )
    app.map.layer["drawing"].layer["polyline"].set_data(app.toolbox["drawing"].polyline)
    update()


def load_polyline(*args: Any) -> None:
    """Load polylines from a GeoJSON file.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    rsp = app.gui.window.dialog_open_file(
        "Select file ...", filter="*.geojson", allow_directory_change=True
    )
    if rsp[0]:
        # Ask if polyline should be added to existing polylines
        if app.gui.getvar("drawing", "nr_polylines") > 0:
            append = app.gui.window.dialog_yes_no("Add to existing polylines?", " ")
        else:
            append = False
        app.toolbox["drawing"].polyline_file_name = rsp[0]
        gdf = gpd.read_file(app.toolbox["drawing"].polyline_file_name)
        # Convert to CRS of app
        gdf = gdf.to_crs(app.crs)
        # Remove all rows where gdf is not a LineString
        gdf = gdf[gdf.geometry.type == "LineString"]
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No polylines found in file", "Error")
            return
        if append:
            # Make sure that gdf has the same crs as app.toolbox["drawing"].polyline
            app.toolbox["drawing"].polyline = pd.concat(
                [app.toolbox["drawing"].polyline, gdf]
            )
        else:
            app.toolbox["drawing"].polyline = gdf
        app.map.layer["drawing"].layer["polyline"].set_data(
            app.toolbox["drawing"].polyline
        )
        update()


def save_polyline(*args: Any) -> None:
    """Save polylines to a GeoJSON file.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=app.toolbox["drawing"].polyline_file_name,
        filter="*.geojson",
        allow_directory_change=True,
    )
    if rsp[0]:
        app.toolbox["drawing"].polyline_file_name = rsp[0]
        # Drop the properties
        gdf = gpd.GeoDataFrame(
            geometry=app.toolbox["drawing"].polyline.geometry
        ).set_crs(app.toolbox["drawing"].polyline.crs)
        gdf.to_file(app.toolbox["drawing"].polyline_file_name, driver="GeoJSON")


def polyline_created(
    gdf: gpd.GeoDataFrame, feature_index: int, feature_id: Any
) -> None:
    """Handle a newly created polyline on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame containing all polylines.
    feature_index : int
        Index of the newly created feature.
    feature_id : Any
        Identifier of the newly created feature.
    """
    app.toolbox["drawing"].polyline = gdf
    app.gui.setvar("drawing", "active_polyline", feature_index)
    update()


def polyline_modified(gdf: gpd.GeoDataFrame, index: int, feature_id: Any) -> None:
    """Handle a modified polyline on the map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Updated GeoDataFrame containing all polylines.
    index : int
        Index of the modified feature.
    feature_id : Any
        Identifier of the modified feature.
    """
    app.toolbox["drawing"].polyline = gdf
    app.gui.setvar("drawing", "active_polyline", index)
    update()


def polyline_selected(index: int) -> None:
    """Handle polyline selection on the map.

    Parameters
    ----------
    index : int
        Index of the selected polyline.
    """
    app.gui.setvar("drawing", "active_polyline", index)
    update()


def edit_polyline_buffer_distance(*args: Any) -> None:
    """Update the temporary layer when the buffer distance changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    update_temp_layer()


def edit_polyline_buffer_distance_left(*args: Any) -> None:
    """Update the temporary layer when the left buffer distance changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    update_temp_layer()


def edit_polyline_buffer_distance_right(*args: Any) -> None:
    """Update the temporary layer when the right buffer distance changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    update_temp_layer()


def edit_polyline_parallel_offset_distance(*args: Any) -> None:
    """Update the temporary layer when the parallel offset distance changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    update_temp_layer()


def apply_buffer(*args: Any) -> None:
    """Generate symmetric buffered polygons from polylines and add to the polygon layer.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["drawing"].asymmetric_buffer = False
    gdf = get_buffered_polylines()
    app.toolbox["drawing"].polygon = concat_gdfs(app.toolbox["drawing"].polygon, gdf)
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()


def apply_asym_buffer(*args: Any) -> None:
    """Generate asymmetric buffered polygons from polylines and add to the polygon layer.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.toolbox["drawing"].asymmetric_buffer = True
    gdf = get_asym_buffered_polylines()
    app.toolbox["drawing"].polygon = concat_gdfs(app.toolbox["drawing"].polygon, gdf)
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()


def apply_parallel_offset(*args: Any) -> None:
    """Generate parallel offset polylines and save to a GeoJSON file.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    distance = app.gui.getvar("drawing", "polyline_parallel_offset_distance")
    gdf = get_parallel_offset_polylines(app.toolbox["drawing"].polyline, distance)
    # Unlike the buffer approach, we do not generate polygons in polygon layer.
    # Here we open a file save menu to save the shifted polylines
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=app.toolbox["drawing"].shifted_polyline_file_name,
        filter="*.geojson",
        allow_directory_change=True,
    )
    if rsp[0]:
        app.toolbox["drawing"].shifted_polyline_file_name = rsp[0]
        gdf.to_file(app.toolbox["drawing"].shifted_polyline_file_name, driver="GeoJSON")

    update()


# def merge_polylines(*args):
#     # Merge polylines
#     geom = app.toolbox["drawing"].polyline.unary_union
#     # get type of geometry
#     if geom.geom_type == "Polyline":
#         geom_list = [geom]
#     else:
#         # Must be a MultiPolyline
#         geom_list = list(geom.geoms)
#     # Check if geom is a MultiPolyline. If so, make it a list of Polylines
#     app.toolbox["drawing"].polyline = gpd.GeoDataFrame(geometry=geom_list).set_crs(app.toolbox["drawing"].polyline.crs)
#     app.map.layer["drawing"].layer["polyline"].set_data(app.toolbox["drawing"].polyline)
#     update()


def update() -> None:
    """Refresh polyline count, names, temp layers, and the GUI window."""
    npol = len(app.toolbox["drawing"].polyline)
    app.gui.setvar("drawing", "nr_polylines", npol)
    iac = app.gui.getvar("drawing", "active_polyline")
    iac = min(iac, npol - 1)
    app.gui.setvar("drawing", "active_polyline", iac)

    # Update polyline names
    update_polyline_names()

    # Update temp layer
    update_temp_layer()

    app.gui.window.update()


def update_polyline_names() -> None:
    """Rebuild the list of polyline display names from the current data."""
    names = []
    for i in range(len(app.toolbox["drawing"].polyline)):
        names.append(f"polyline_{i + 1}")
    app.gui.setvar("drawing", "polyline_names", names)


def update_temp_layer() -> None:
    """Refresh all temporary preview layers for buffers and parallel offsets."""
    # Clear temp layer
    layer = app.map.layer["drawing"].layer["polyline_tmp"]
    layer.clear()

    if len(app.toolbox["drawing"].polyline) > 0:
        # Do both symmetric and asymmetric buffers

        # Regular
        buffer_distance = app.gui.getvar("drawing", "polyline_buffer_distance")
        if buffer_distance > 0.0:
            # Loop through polylines
            gdf = get_buffered_polylines()
            # Add to temp layer
            layer.set_data(gdf)

    # Clear temp layer
    layer = app.map.layer["drawing"].layer["polyline_asym_tmp"]
    layer.clear()

    if len(app.toolbox["drawing"].polyline) > 0:
        # Asymmetric
        buffer_distance_left = app.gui.getvar(
            "drawing", "polyline_buffer_distance_left"
        )
        buffer_distance_right = app.gui.getvar(
            "drawing", "polyline_buffer_distance_right"
        )
        if buffer_distance_left > 0.0 or buffer_distance_right > 0.0:
            # Loop through polylines
            gdf = get_asym_buffered_polylines()
            # Add to temp layer
            layer.set_data(gdf)

    # Clear temp layer
    layer = app.map.layer["drawing"].layer["polyline_parallel_offset_tmp"]
    layer.clear()

    if len(app.toolbox["drawing"].polyline) > 0:
        # Parallel offset
        distance = app.gui.getvar("drawing", "polyline_parallel_offset_distance")
        if abs(distance) > 0.0:
            # Loop through polylines
            gdf = get_parallel_offset_polylines(
                app.toolbox["drawing"].polyline, distance
            )
            # Add to temp layer
            layer.set_data(gdf)


def get_buffered_polylines() -> gpd.GeoDataFrame:
    """Compute symmetric buffer polygons around all polylines.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with buffered polygon geometries.
    """
    buffer_distance = app.gui.getvar("drawing", "polyline_buffer_distance")
    simplify_tolerance = 0.1 * buffer_distance
    # Check if gdf is in geographic or projected CRS
    if app.toolbox["drawing"].polyline.crs.is_geographic:
        # Convert to Azimuthal equidistant projection
        lon = app.toolbox["drawing"].polyline.centroid.x.mean()
        lat = app.toolbox["drawing"].polyline.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
        )
        geom = app.toolbox["drawing"].polyline.to_crs(aeqd_proj).buffer(buffer_distance)
        geom = geom.simplify(tolerance=simplify_tolerance)
        # Simplify
        gdf = (
            gpd.GeoDataFrame(geom, columns=["geometry"])
            .set_crs(aeqd_proj)
            .to_crs(app.toolbox["drawing"].polyline.crs)
        )
    else:
        geom = app.toolbox["drawing"].polyline.buffer(buffer_distance)
        geom = geom.simplify(tolerance=simplify_tolerance)
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).to_crs(
            app.toolbox["drawing"].polyline.crs
        )

    return gdf


def get_asym_buffered_polylines() -> gpd.GeoDataFrame:
    """Compute asymmetric (left/right) buffer polygons around all polylines.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with asymmetrically buffered polygon geometries.
    """
    buffer_distance_left = app.gui.getvar("drawing", "polyline_buffer_distance_left")
    buffer_distance_right = app.gui.getvar("drawing", "polyline_buffer_distance_right")
    simplify_tolerance = 0.1 * max(buffer_distance_left, buffer_distance_right)
    # Check if gdf is in geographic or projected CRS
    if app.toolbox["drawing"].polyline.crs.is_geographic:
        # Convert to Azimuthal equidistant projection
        lon = app.toolbox["drawing"].polyline.centroid.x.mean()
        lat = app.toolbox["drawing"].polyline.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
        )

        line = app.toolbox["drawing"].polyline.to_crs(aeqd_proj)
        left = line.buffer(buffer_distance_left, single_sided=True)
        right = line.buffer(-buffer_distance_right, single_sided=True)
        geom = unary_union([left, right])
        geom = geom.simplify(tolerance=simplify_tolerance)
        # if geom is a multipolygon, turn into multiple polygons
        if geom.geom_type == "MultiPolygon":
            geom = list(geom.geoms)
        else:
            geom = [geom]
        gdf = (
            gpd.GeoDataFrame(geom, columns=["geometry"])
            .set_crs(aeqd_proj)
            .to_crs(app.toolbox["drawing"].polyline.crs)
        )

    else:
        line = app.toolbox["drawing"].polyline
        left = line.buffer(buffer_distance_left, single_sided=True)
        right = line.buffer(-buffer_distance_right, single_sided=True)
        geom = unary_union([left, right])
        geom = geom.simplify(tolerance=simplify_tolerance)
        # if geom is a multipolygon, turn into multiple polygons
        if geom.geom_type == "MultiPolygon":
            geom = list(geom.geoms)
        else:
            geom = [geom]
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).set_crs(
            app.toolbox["drawing"].polyline.crs
        )

    return gdf


def get_parallel_offset_polylines(
    gdf: gpd.GeoDataFrame, offset_distance: float
) -> gpd.GeoDataFrame:
    """Compute parallel offset lines for all polylines in the GeoDataFrame.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Input polylines to offset.
    offset_distance : float
        Offset distance. Negative values offset to the left, positive to the right.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with offset line geometries.
    """
    # If gdf is empty, return empty gdf
    if len(gdf) == 0:
        return gpd.GeoDataFrame()

    if offset_distance < 0.0:
        side = "left"
    else:
        side = "right"
    offset_distance = abs(offset_distance)

    if gdf.crs.is_geographic:
        # Loop through line_list and convert to Azimuthal equidistant projection
        lon = gdf.centroid.x.mean()
        lat = gdf.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
            f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0"
        )
        gdf_local = gdf.to_crs(aeqd_proj)
    else:
        gdf_local = gdf

    # Make list of linestring geometries
    line_list = gdf_local[gdf_local.geom_type == "LineString"].geometry.tolist()

    # Now apply parallel offset to each line
    line_list = [line.parallel_offset(offset_distance, side=side) for line in line_list]

    if gdf.crs.is_geographic:
        gdf_out = (
            gpd.GeoDataFrame(line_list, columns=["geometry"])
            .set_crs(aeqd_proj)
            .to_crs(gdf.crs)
        )
    else:
        gdf_out = gpd.GeoDataFrame(line_list, columns=["geometry"]).set_crs(gdf.crs)

    return gdf_out


def concat_gdfs(gdf0: gpd.GeoDataFrame, gdf1: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Concatenate two GeoDataFrames, projecting both to the map CRS.

    Parameters
    ----------
    gdf0 : gpd.GeoDataFrame
        First GeoDataFrame.
    gdf1 : gpd.GeoDataFrame
        Second GeoDataFrame.

    Returns
    -------
    gpd.GeoDataFrame
        Concatenated GeoDataFrame in the map CRS.
    """
    # Check if gdf0 is empty
    if len(gdf0) == 0:
        return gdf1.to_crs(app.map.crs)
    # Check if gdf1 is empty
    if len(gdf1) == 0:
        return gdf0.to_crs(app.map.crs)
    # Concatenate and reset index
    return pd.concat([gdf0.to_crs(app.map.crs), gdf1.to_crs(app.map.crs)]).reset_index(
        drop=True
    )
