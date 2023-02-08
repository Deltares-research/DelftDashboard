# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb
from cht.bathymetry.bathymetry_database import bathymetry_database
from guitools.gui import find_element_by_id

def map_ready():

    # This method is called when the map has been loaded
    print('Map is ready !')

    # Find map widget
    ddb.gui.map_widget = {}
    element = find_element_by_id(ddb.gui.config["element"], "map")
    ddb.gui.map_widget["map"] = element["widget_group"]

    mp = ddb.gui.map_widget["map"]

    # Add main DDB layer
    main_layer = mp.add_layer("main")

    # Add background topography layer
    ddb.background_topography_layer = main_layer.add_raster_layer("background_topography")

    # Set update method for topography layer
    ddb.background_topography_layer.update = update_background

    # Go to point
    mp.jump_to(5.0, 52.0, 5)

    ddb.on_map_ready()


def map_moved(coords):
    # This method is called whenever the location of the map changes
    # Layers are already automatically updated in MapBox
    pass


def update_background():

    mp = ddb.gui.map_widget["map"]

    if not mp.map_extent:
        print("Map extent not yet available ...")
        return

    coords = mp.map_extent
    if ddb.auto_update_topography:
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        dxmax = 900.0
        maxcellsize = (xl[1] - xl[0]) / dxmax
        maxcellsize *= 111111
        try:
            x, y, z = bathymetry_database.get_data(ddb.background_topography,
                                                   xl,
                                                   yl,
                                                   maxcellsize)
            ddb.background_topography_layer.set_data(x=x, y=y, z=z, colormap=ddb.color_map_earth, decimals=0)
        except:
            print("Error loading background topo ...")

def update():
    ddb.gui.map_widget["map"].set_mouse_default()
    # Sets all layers to inactive
    for name, model in ddb.model.items():
        model.plot()
    for name, toolbox in ddb.toolbox.items():
        toolbox.update_map("deactivate")
