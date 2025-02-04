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
    app.map.layer["drawing"].layer["polygon"].show()
    app.map.layer["drawing"].layer["polygon"].activate()
    app.map.layer["drawing"].layer["polygon_tmp"].show()
    update()

def draw_polygon(*args):
    layer = app.map.layer["drawing"].layer["polygon"]
    layer.draw()

def select_polygon(*args):
    # Polygon selected from list
    iac = app.gui.getvar("drawing", "active_polygon")
    # Activate on map
    app.map.layer["drawing"].layer["polygon"].activate_feature(iac)

def delete_polygon(*args):
    # if app.toolbox["drawing"].polygon:
    iac = app.gui.getvar("drawing", "active_polygon")
    # Remove polygon with index iac from gdf
    app.toolbox["drawing"].polygon = app.toolbox["drawing"].polygon.drop(index=iac).reset_index(drop=True)
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()

def load_polygon(*args):
    # Load polygon from geojson file
    # Get the file name
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          filter="*.geojson",
                                          allow_directory_change=True)
    if rsp[0]:
        # Ask if polygon should be added to existing polygons
        if app.gui.getvar("drawing", "nr_polygons") > 0:
            append = app.gui.window.dialog_yes_no("Add to existing polygons?", " ")
        else:
            append = False
        app.toolbox["drawing"].polygon_file_name = rsp[0]
        gdf = gpd.read_file(app.toolbox["drawing"].polygon_file_name)
        # Remove all rows where gdf is not a Polygon
        gdf = gdf[gdf.geometry.type == "Polygon"]
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No polygons found in file", "Error")
            return
        # Change all polygons in gdf to polylines ?
        if append:
            # Make sure that gdf has the same crs as app.toolbox["drawing"].polygon
            gdf = gdf.to_crs(app.toolbox["drawing"].polygon.crs)
            app.toolbox["drawing"].polygon = pd.concat([app.toolbox["drawing"].polygon, gdf])
        else:
            app.toolbox["drawing"].polygon = gdf
        app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
        update()

def save_polygon(*args):
    # Save polygon to geojson file
    # Get the file name
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=app.toolbox["drawing"].polygon_file_name,
                                          filter="*.geojson",
                                          allow_directory_change=True)
    if rsp[0]:
        app.toolbox["drawing"].polygon_file_name = rsp[0]
        # Drop the properties
        gdf = gpd.GeoDataFrame(geometry=app.toolbox["drawing"].polygon.geometry).set_crs(app.toolbox["drawing"].polygon.crs)
        gdf.to_file(app.toolbox["drawing"].polygon_file_name, driver="GeoJSON")

def polygon_created(gdf, feature_index, feature_id):
    # Polygon was added on map
    app.toolbox["drawing"].polygon = gdf
    app.gui.setvar("drawing", "active_polygon", feature_index)
    update()

def polygon_modified(gdf, index, feature_id):
    app.toolbox["drawing"].polygon = gdf
    app.gui.setvar("drawing", "active_polygon", index)
    update()

def polygon_selected(index):
    # Polygon selected on map
    app.gui.setvar("drawing", "active_polygon", index)
    update()

def edit_polygon_buffer_distance(*args):
    # Buffer distance changed
    update_temp_layer()

def apply_buffer(*args):
    gdf = get_buffered_polygons()
    app.toolbox["drawing"].polygon = gdf
    # Change polygon in draw layer
    app.map.layer["drawing"].layer["polygon"].set_data(gdf)
    # Set buffer to 0.0, so that temp layer will be cleared
    app.gui.setvar("drawing", "polygon_buffer_distance", 0.0)
    update()

def merge_polygons(*args):
    # Merge polygons
    geom = app.toolbox["drawing"].polygon.unary_union
    # Check if geom is a MultiPolygon. If so, make it a list of Polygons
    if geom.geom_type == "Polygon":
        geom_list = [geom]
    else:
        # Must be a MultiPolygon
        geom_list = list(geom.geoms)
    app.toolbox["drawing"].polygon = gpd.GeoDataFrame(geometry=geom_list).set_crs(app.toolbox["drawing"].polygon.crs)
    app.map.layer["drawing"].layer["polygon"].set_data(app.toolbox["drawing"].polygon)
    update()

def update():

    npol = len(app.toolbox["drawing"].polygon)
    app.gui.setvar("drawing", "nr_polygons", npol)
    iac = app.gui.getvar("drawing", "active_polygon")
    iac = max(min(iac, npol - 1), 0)
    app.gui.setvar("drawing", "active_polygon", iac)

    # Update polygon names
    update_polygon_names()

    # Update temp layer
    update_temp_layer()

    app.gui.window.update()

def update_polygon_names():
    names = []
    for i in range(len(app.toolbox["drawing"].polygon)):
        names.append("polygon_" + str(i + 1))
    app.gui.setvar("drawing", "polygon_names", names)    

def update_temp_layer():
    # Clear temp layer
    layer = app.map.layer["drawing"].layer["polygon_tmp"]
    layer.clear()
    if len(app.toolbox["drawing"].polygon) > 0:
        buffer_distance = app.gui.getvar("drawing", "polygon_buffer_distance")
        if buffer_distance > 0.0:
            # Loop through polygons
            gdf = get_buffered_polygons()
            # Add to temp layer
            layer.set_data(gdf)

def get_buffered_polygons():
    buffer_distance = app.gui.getvar("drawing", "polygon_buffer_distance")
    # Check if gdf is in geographic or projected CRS
    if app.toolbox["drawing"].polygon.crs.is_geographic:
        # Convert to Azimuthal equidistant projection
        lon = app.toolbox["drawing"].polygon.centroid.x.mean()
        lat = app.toolbox["drawing"].polygon.centroid.y.mean()
        aeqd_proj = CRS.from_proj4(
                f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")                
        geom = app.toolbox["drawing"].polygon.to_crs(aeqd_proj).buffer(buffer_distance)
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).set_crs(aeqd_proj).to_crs(app.toolbox["drawing"].polygon.crs)
    else:
        geom = app.toolbox["drawing"].polygon.buffer(buffer_distance)
        gdf = gpd.GeoDataFrame(geom, columns=["geometry"]).to_crs(app.toolbox["drawing"].polygon.crs)

    return gdf
