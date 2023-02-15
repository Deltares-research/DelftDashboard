# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import numpy as np

from ddb import ddb
from cht.bathymetry.bathymetry_database import bathymetry_database
from guitares.gui import find_element_by_id
from cht.misc.geometry import RegularGrid
from pyproj import CRS

def map_ready():

    # This method is called when the map has been loaded
    print('Map is ready !')

    # Find map widget
    element = find_element_by_id(ddb.gui.config["element"], "map")
    ddb.map = element["widget"]

    # Add main DDB layer
    main_layer = ddb.map.add_layer("main")

    # Add background topography layer
    ddb.background_topography_layer = main_layer.add_raster_layer("background_topography")

    # Set update method for topography layer
    ddb.background_topography_layer.update = update_background

    # Go to point
    ddb.map.jump_to(0.0, 0.0, 2)

    # Add layers to map (we can only do this after the map has finished loading)
    for name, model in ddb.model.items():
        model.add_layers()
    for name, toolbox in ddb.toolbox.items():
        toolbox.add_layers()

    # Default model is first model in config
    model_name = list(ddb.model.keys())[0]
    # Select this model (this will update the menu and add the toolbox)
    ddb.model[model_name].select()

    ddb.gui.close_splash()

def map_moved(coords):
    # This method is called whenever the location of the map changes
    # Layers are already automatically updated in MapBox
    pass


def update_background():

    if not ddb.map.map_extent:
        print("Map extent not yet available ...")
        return

    if ddb.auto_update_topography and ddb.view["topography"]["visible"]:
        coords = ddb.map.map_extent
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        if ddb.view["topography"]["quality"] == "high":
            npix = ddb.gui.window.width()
        elif ddb.view["topography"]["quality"] == "medium":
            npix = int(ddb.gui.window.width()*0.5)
        else:
            npix = int(ddb.gui.window.width()*0.25)

        dxy = (xl[1] - xl[0])/npix
        xv = np.arange(xl[0], xl[1], dxy)
        yv = np.arange(yl[0], yl[1], dxy)
        dataset = bathymetry_database.get_dataset(ddb.background_topography)
        dataset_list = [{"dataset": dataset, "zmin": -99999.9, "zmax": 99999.9}]

        try:
            z = bathymetry_database.get_bathymetry_on_grid(xv, yv, CRS(4326), dataset_list,
                                                           method=ddb.view["topography"]["interp_method"])
            ddb.background_topography_layer.set_data(x=xv, y=yv, z=z, colormap=ddb.color_map_earth, decimals=0)
        except:
            print("Error loading background topo ...")
        # try:
        #     x, y, z = bathymetry_database.get_data(ddb.background_topography,
        #                                            xl,
        #                                            yl,
        #                                            maxcellsize)
        #     ddb.background_topography_layer.set_data(x=x, y=y, z=z, colormap=ddb.color_map_earth, decimals=0)
        # except:
        #     print("Error loading background topo ...")

def update():
    ddb.map.set_mouse_default()
    # Sets all layers to inactive
    for name, model in ddb.model.items():
        model.plot()
    for name, toolbox in ddb.toolbox.items():
        toolbox.update_map("deactivate")
