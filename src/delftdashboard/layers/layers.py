# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import numpy as np
import traceback
from pyproj import CRS
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map
from cht_bathymetry.utils import get_isobaths, add_buffer
# from cht_bathymetry.bathymetry_database import bathymetry_database

def select(*args):
    # De-activate existing layers
    aux_layer = app.map.add_layer("aux_layer")
    aux_layer.add_layer("shoreline", type="line", line_color="red", circle_radius=2)
    aux_layer.add_layer("polygon", type="line")
    map.update()


def push(*args):
    buffer_size = app.gui.getvar("layers", "buffer_size")
    buffer_land = app.gui.getvar("layers", "buffer_land")
    buffer_sea = app.gui.getvar("layers", "buffer_sea")
    contour_elevation = app.gui.getvar("layers", "contour_elevation")
    buffer_single = app.gui.getvar("layers", "buffer_single")

    coords = app.map.map_extent
    xl = [coords[0][0], coords[1][0]]
    yl = [coords[0][1], coords[1][1]]
    wdt = app.map.view.geometry().width()
    npix = wdt

    dxy = (xl[1] - xl[0])/npix
    xv = np.arange(xl[0], xl[1], dxy)
    yv = np.arange(yl[0], yl[1], dxy)
    dataset = bathymetry_database.get_dataset(app.background_topography)
    dataset_list = [{"dataset": dataset, "zmin": -99999.9, "zmax": 99999.9}]

    try:
        z = bathymetry_database.get_bathymetry_on_grid(xv, yv, CRS(4326), dataset_list,
                                                        method=app.view["topography"]["interp_method"])
    except:
        print("Error loading background topo ...")
        traceback.print_exc()    


    shoreline_gdf  = get_isobaths(xv, yv, z, contour_elevation, CRS(4326))
#    refinement_gdf = add_buffer(shoreline_gdf, 10000.0)
    refinement_gdf = add_buffer(shoreline_gdf, buffer_land=buffer_land, buffer_sea=buffer_sea, simplify=0.0)
    # Compute union of all polygons in refinement_gdf and return as gdf (should add this to add_buffer function)
#    refinement_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(refinement_gdf.unary_union)).set_crs(CRS(4326)).explode().loc[0]
    app.map.layer["aux_layer"].layer["polygon"].set_data(refinement_gdf)
    app.map.layer["aux_layer"].layer["shoreline"].set_data(shoreline_gdf)

#    # Add buffer around isobaths (this returns gdf with polygons)
#    refinement_gdf = add_buffer(shoreline_gdf, refdist, simplify=0.02)
