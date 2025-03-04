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
# from cht_bathymetry.bathymetry_database import bathymetry_database

def map_ready(*args):

    # This method is called when the map has been loaded
    print('Map is ready ! Adding background topography and other layers ...')

    # Find map widget
    element = app.gui.window.find_element_by_id("map")
    app.map = element.widget

    # Add main DDB layer
    main_layer = app.map.add_layer("main")

    # Add background topography layer
    main_layer.add_layer("background_topography", type="raster")
    # app.background_topography_layer = main_layer.add_layer("background_topography", type="raster")

    # Set update method for topography layer
    app.map.layer["main"].layer["background_topography"].update = update_background_topography_layer
    # app.background_topography_layer.update = update_background_topography_layer

    # Go to point
    app.map.jump_to(0.0, 0.0, 1)

    # Add layers to map (we can only do this after the map has finished loading)
    for name, model in app.model.items():
        model.add_layers()
    for name, toolbox in app.toolbox.items():
        toolbox.add_layers()

    # Default model is first model in config
    model_name = list(app.model.keys())[0]

    # Select this model (this will update the menu and add the toolbox)
    app.model[model_name].select()

    update_statusbar()

    app.gui.close_splash()

def map_moved(coords, widget):
    # This method is called whenever the location of the map changes
    # Layers are already automatically updated in MapBox
    pass

def mouse_moved(x, y, lon, lat):
    # This method is called whenever the mouse moves over the map
    # We can use this to show the coordinates of the mouse in the status bar
    if app.map.crs.is_geographic:
        app.gui.window.statusbar.set_text("lon", f"Lon : {lon:.6f}")
        app.gui.window.statusbar.set_text("lat", f"Lat : {lat:.6f}")
        app.gui.window.statusbar.set_text("x", "X :")
        app.gui.window.statusbar.set_text("y", "Y :")
    else:
        app.gui.window.statusbar.set_text("lon", f"Lon : {lon:.6f}")
        app.gui.window.statusbar.set_text("lat", f"Lat : {lat:.6f}")
        app.gui.window.statusbar.set_text("x", f"X : {x:.1f}")
        app.gui.window.statusbar.set_text("y", f"Y : {y:.1f}")

def update_background_topography_layer():

    # Function that is called whenever the map has moved

    if not app.map.map_extent:
        print("Map extent not yet available ...")
        return

    try:

        auto_update = app.gui.getvar("view_settings", "topography_auto_update")
        visible = app.gui.getvar("view_settings", "topography_visible")
        quality = app.gui.getvar("view_settings", "topography_quality")
        colormap = app.gui.getvar("view_settings", "topography_colormap")
        interp_method = app.gui.getvar("view_settings", "topography_interp_method")
        opacity = app.gui.getvar("view_settings", "topography_opacity")
        zmin = app.gui.getvar("view_settings", "topography_zmin")
        zmax = app.gui.getvar("view_settings", "topography_zmax")
        autoscaling = app.gui.getvar("view_settings", "topography_autoscaling")
        hillshading = app.gui.getvar("view_settings", "topography_hillshading")

        if auto_update and visible:

            print("Updating background topography ...")

            coords = app.map.map_extent
            xl = [coords[0][0], coords[1][0]]
            yl = [coords[0][1], coords[1][1]]
            wdt = app.map.view.geometry().width()
            if quality == "high":
                npix = wdt
            elif quality == "medium":
                npix = int(wdt*0.5)
            else:
                npix = int(wdt*0.25)

            dxy = (xl[1] - xl[0])/npix
            xv = np.arange(xl[0], xl[1], dxy)
            yv = np.arange(yl[0], yl[1], dxy)
            background_topography_dataset = app.gui.getvar("view_settings", "topography_dataset")
            dataset_list = [{"name": background_topography_dataset, "zmin": -99999.9, "zmax": 99999.9}]

            try:
                cmap = mpl.cm.get_cmap(colormap)
                # Add wait box
                z = app.bathymetry_database.get_bathymetry_on_grid(xv, yv, CRS(4326), dataset_list,
                                                                   method=interp_method,
                                                                   waitbox=app.gui.window.dialog_wait)

                app.map.layer["main"].layer["background_topography"].opacity = opacity

                app.map.layer["main"].layer["background_topography"].color_scale_auto = autoscaling
                app.map.layer["main"].layer["background_topography"].color_scale_symmetric = True
                app.map.layer["main"].layer["background_topography"].color_scale_symmetric_side = "min"
                app.map.layer["main"].layer["background_topography"].color_scale_cmin = zmin
                app.map.layer["main"].layer["background_topography"].color_scale_cmax = zmax
                app.map.layer["main"].layer["background_topography"].hillshading = hillshading

                app.map.layer["main"].layer["background_topography"].set_data(x=xv, y=yv, z=z, colormap=cmap, decimals=0)

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
        # The active model is set to inactive, the rest to invisible
        if model == app.active_model:
            model.set_layer_mode("inactive")
        else:
            model.set_layer_mode("invisible")
    for name, toolbox in app.toolbox.items():
        # The active toolbox is set to inactive, the rest to invisible
        if toolbox == app.active_toolbox:
            toolbox.set_layer_mode("inactive")
        else:
            toolbox.set_layer_mode("invisible")
    app.map.close_popup()        

def reset_cursor():
    app.map.set_mouse_default()

def set_crs(crs):
    app.crs = crs
    app.map.crs = crs
    update_statusbar()

def update_statusbar():
    # Update the status bar with the current CRS
    if app.crs.is_geographic:
        crstp = " (geographic) - " + app.crs.to_string()
        # app.gui.window.statusbar.set_text("crs_type", "geographic")
    else:
        crstp = " (projected) - " + app.crs.to_string()
        # app.gui.window.statusbar.set_text("crs_type", "projected")
    app.gui.window.statusbar.set_text("crs_name", "   " + app.crs.name + crstp)
    # app.gui.window.statusbar.set_text("crs_code", app.crs.to_string())
