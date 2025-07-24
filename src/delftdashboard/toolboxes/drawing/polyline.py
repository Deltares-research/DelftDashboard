# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd
import pandas as pd
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks

def select(*args):
    # Tab selected
    # De-activate() existing layers
    map.update()
    app.map.layer["drawing"].show()
    app.map.layer["drawing"].layer["polyline"].activate()
    app.map.layer["drawing"].layer["polyline_tmp"].show()

def draw_polyline(*args):
    layer = app.map.layer["drawing"].layer["polyline"]
    layer.draw()

def select_polyline(*args):
    # Polyline selected from list
    iac = app.gui.getvar("drawing", "active_polyline")
    # Activate on map
    app.map.layer["drawing"].layer["polyline"].activate_feature(iac)

def delete_polyline(*args):
    # if app.toolbox["drawing"].polyline:
    iac = app.gui.getvar("drawing", "active_polyline")
    # Remove polyline with index iac from gdf
    app.toolbox["drawing"].polyline = app.toolbox["drawing"].polyline.drop(index=iac).reset_index(drop=True)
    app.map.layer["drawing"].layer["polyline"].set_data(app.toolbox["drawing"].polyline)
    update()


def load_polyline(*args):
    # Load polygon from geojson file
    # Get the file name
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          filter="*.geojson",
                                          allow_directory_change=True)
    if rsp[0]:
        # Ask if polyline should be added to existing polylines
        if app.gui.getvar("drawing", "nr_polylines") > 0:
            append = app.gui.window.dialog_yes_no("Add to existing polylines?", " ")
        else:
            append = False
        app.toolbox["drawing"].polyline_file_name = rsp[0]
        gdf = gpd.read_file(app.toolbox["drawing"].polyline_file_name)
        # Remove all rows where gdf is not a LineString
        gdf = gdf[gdf.geometry.type == "LineString"]
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No polylines found in file", "Error")
            return
        if append:
            # Make sure that gdf has the same crs as app.toolbox["drawing"].polyline
            gdf = gdf.to_crs(app.toolbox["drawing"].polyline.crs)
            app.toolbox["drawing"].polyline = pd.concat([app.toolbox["drawing"].polyline, gdf])
        else:
            app.toolbox["drawing"].polyline = gdf
        app.map.layer["drawing"].layer["polyline"].set_data(app.toolbox["drawing"].polyline)
        update()

def save_polyline(*args):
    # Save polyline to geojson file
    # Get the file name
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=app.toolbox["drawing"].polyline_file_name,
                                          filter="*.geojson",
                                          allow_directory_change=True)
    if rsp[0]:
        app.toolbox["drawing"].polyline_file_name = rsp[0]
        # Drop the properties
        gdf = gpd.GeoDataFrame(geometry=app.toolbox["drawing"].polyline.geometry).set_crs(app.toolbox["drawing"].polyline.crs)
        gdf.to_file(app.toolbox["drawing"].polyline_file_name, driver="GeoJSON")


def polyline_created(gdf, feature_index, feature_id):
    # Polyline was added on map
    app.toolbox["drawing"].polyline = gdf
    app.gui.setvar("drawing", "active_polyline", feature_index)
    update()

def polyline_modified(gdf, index, feature_id):
    app.toolbox["drawing"].polyline = gdf
    app.gui.setvar("drawing", "active_polyline", index)
    update()

def polyline_selected(index):
    # Polyline selected on map
    app.gui.setvar("drawing", "active_polyline", index)
    update()

def edit_polyline_buffer_distance(*args):
    # Buffer distance changed
    update_temp_layer()

def apply_buffer(*args):
    # Generate buffered polylines and add them to polygon layer
    gdf = get_buffered_polylines()
    app.toolbox["drawing"].polygon = pd.concat([app.toolbox["drawing"].polygon, gdf])
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)


    # app.toolbox["drawing"].polyline = gdf
    # # Change polyline in draw layer
    # app.map.layer["drawing"].layer["polyline"].set_data(gdf)
    # Set buffer to 0.0, so that temp layer will be cleared
    # app.gui.setvar("drawing", "polyline_buffer_distance", 0.0)
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

def update():

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

def update_polyline_names():
    names = []
    for i in range(len(app.toolbox["drawing"].polyline)):
        names.append("polyline_" + str(i + 1))
    app.gui.setvar("drawing", "polyline_names", names)    

def update_temp_layer():
    # Clear temp layer
    layer = app.map.layer["drawing"].layer["polyline_tmp"]
    layer.clear()
    if len(app.toolbox["drawing"].polyline) > 0:
        buffer_distance = app.gui.getvar("drawing", "polyline_buffer_distance")
        if buffer_distance > 0.0:
            # Loop through polylines
            gdf = get_buffered_polylines()
            # Add to temp layer
            layer.set_data(gdf)

def get_buffered_polylines():
    buffer_distance = app.gui.getvar("drawing", "polyline_buffer_distance")
    simplify_tolerance = 0.2 * buffer_distance
    # Check if gdf is in geographic or projected CRS
    if app.toolbox["drawing"].polyline.crs.is_geographic:
        # Convert to Azimuthal equidistant projection
        lon = app.toolbox["drawing"].polyline.centroid.x.mean()
        lat = app.toolbox["drawing"].polyline.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
                f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")                
        geom = app.toolbox["drawing"].polyline.to_crs(aeqd_proj).buffer(buffer_distance)
        geom = geom.simplify(tolerance=simplify_tolerance)
        # Simplify
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).set_crs(aeqd_proj).to_crs(app.toolbox["drawing"].polyline.crs)
    else:
        geom = app.toolbox["drawing"].polyline.buffer(buffer_distance)
        geom = geom.simplify(tolerance=simplify_tolerance)
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).to_crs(app.toolbox["drawing"].polyline.crs)

    return gdf
