# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import numpy as np
import traceback
from pyproj import CRS
import matplotlib as mpl

from delftdashboard.app import app
from cht_bathymetry.bathymetry_database import bathymetry_database
# from cht_utils.geometry import RegularGrid

def map_ready(*args):

    # This method is called when the map has been loaded
    print('Map is ready !')

    # Find map widget
    element = app.gui.window.find_element_by_id("map")
    app.map = element.widget

    # Add main DDB layer
    main_layer = app.map.add_layer("main")

    # Add background topography layer
    app.background_topography_layer = main_layer.add_layer("background_topography", type="raster")

    # Set update method for topography layer
    app.background_topography_layer.update = update_background

    # Go to point
    app.map.jump_to(0.0, 0.0, 2)

    # Add layers to map (we can only do this after the map has finished loading)
    for name, model in app.model.items():
        model.add_layers()
    for name, toolbox in app.toolbox.items():
        toolbox.add_layers()

    # Default model is first model in config
    model_name = list(app.model.keys())[0]

    # Select this model (this will update the menu and add the toolbox)
    app.model[model_name].select()

    app.gui.close_splash()

def map_moved(coords, widget):
    # This method is called whenever the location of the map changes
    # Layers are already automatically updated in MapBox
    pass


def update_background():

    # Function that is called whenever the map has moved

    if not app.map.map_extent:
        print("Map extent not yet available ...")
        return

    try:

        if app.auto_update_topography and app.view["topography"]["visible"]:

            print("Updating background topography ...")

            coords = app.map.map_extent
            xl = [coords[0][0], coords[1][0]]
            yl = [coords[0][1], coords[1][1]]
            wdt = app.map.view.geometry().width()
            if app.view["topography"]["quality"] == "high":
                npix = wdt
            elif app.view["topography"]["quality"] == "medium":
                npix = int(wdt*0.5)
            else:
                npix = int(wdt*0.25)

            dxy = (xl[1] - xl[0])/npix
            xv = np.arange(xl[0], xl[1], dxy)
            yv = np.arange(yl[0], yl[1], dxy)
            dataset = bathymetry_database.get_dataset(app.background_topography)
            dataset_list = [{"dataset": dataset, "zmin": -99999.9, "zmax": 99999.9}]

            try:
                cmap = mpl.cm.get_cmap(app.view["topography"]["colormap"])
                z = bathymetry_database.get_bathymetry_on_grid(xv, yv, CRS(4326), dataset_list,
                                                            method=app.view["topography"]["interp_method"])
                app.background_topography_layer.set_data(x=xv, y=yv, z=z, colormap=cmap, decimals=0)
            except:
                print("Error loading background topo ...")
                traceback.print_exc()

                print("Updating background topography done.")

    except:
        print("Error updating background topo ...")
        traceback.print_exc()

def update():
    reset_cursor()
    # Sets all layers to inactive
    for name, model in app.model.items():
        if model == app.active_model:
            model.set_layer_mode("inactive")
        else:
            model.set_layer_mode("invisible")
    for name, toolbox in app.toolbox.items():
        if toolbox == app.active_toolbox:
            toolbox.set_layer_mode("inactive")
        else:
            toolbox.set_layer_mode("invisible")

def reset_cursor():
    app.map.set_mouse_default()
