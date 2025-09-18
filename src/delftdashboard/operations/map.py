# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import numpy as np
import xarray as xr
import traceback
from pyproj import CRS, Transformer
# import matplotlib as mpl

from delftdashboard.app import app

transformer_4326_to_3857 = Transformer.from_crs(CRS(4326), CRS(3857), always_xy=True)

def map_ready(*args):

    # This method is called when the map has been loaded
    print('Map is ready ! Adding background topography and other layers ...')

    # Find map widget
    element = app.gui.window.find_element_by_id("map")
    app.map = element.widget

    # Add main DDB layer
    main_layer = app.map.add_layer("main")

    # Add background topography layer
    main_layer.add_layer("background_topography",
                         type="raster_image")

    # Set update method for topography layer (this is called in the layer's update method!)
    # app.map.layer["main"].layer["background_topography"].get_data = update_background_topography_data
    app.map.layer["main"].layer["background_topography"].set_data(update_background_topography_data)
    app.map.layer["main"].layer["background_topography"].legend_position = "bottom-left"

    # Go to point
    app.map.jump_to(0.0, 0.0, 0.5)

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

    app.gui.window.resize() # Need to do this in order to get the correct size of the widgets. Should really be done by Guitares, but for some reason it does not work there.

    app.gui.close_splash()

def map_moved(coords, widget):
    # This method is called whenever the location of the map changes
    # Layers are already automatically updated in MapBox
    pass

def mouse_moved(x, y, lon, lat):
    # This method is called whenever the mouse moves over the map
    # We can use this to show the coordinates of the mouse in the status bar
    
    # Check if the map is ready (it's possible that the map is not yet ready when this method is called)
    if not hasattr(app, "map"):
        return

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

    x3857, y3857 = transformer_4326_to_3857.transform(lon, lat) 

    z = np.nan
    if hasattr(app, "background_topography") and app.background_topography is not None:
        # Get the z value at the mouse position
        try:
            z = app.background_topography.sel(x=x3857, y=y3857, method="nearest").item()
        except Exception as e:
            z = np.nan
            print(f"Error getting z value: {e}")

    if np.isnan(z):
        app.gui.window.statusbar.set_text("z", "Z : N/A")
    else:       
        app.gui.window.statusbar.set_text("z", f"Z : {z:.2f} m")


def update_background_topography_data():

    # Function that is called whenever the map has moved
    da = None

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

            coords = app.map.map_extent

            hgt = app.map.view.geometry().height()
            if quality == "high":
                npix = hgt
            elif quality == "medium":
                npix = int(hgt*0.5)
            else:
                npix = int(hgt*0.25)

            # Actually easiest to use web mercator
            # transformer_4326_to_3857 = Transformer.from_crs(CRS(4326), CRS(3857), always_xy=True)
            if coords[1][0] - coords[0][0] > 360.0:
                # If the map is larger than 360 degrees, we can make image of entire world
                coords[0][0] = -180.0
                coords[1][0] = 180.0
            x0, y0 = transformer_4326_to_3857.transform(coords[0][0], coords[0][1])
            x1, y1 = transformer_4326_to_3857.transform(coords[1][0], coords[1][1])
            if x0 > x1:
                # Subtract max size of web mercator
                x0 -= 40075016.68557849
            if x0 < -20037508.342789244:
                # Add max size of web mercator
                x0 += 40075016.68557849
                x1 += 40075016.68557849    
            xl = [x0, x1]
            yl = [y0, y1]

            dxy = (yl[1] - yl[0]) / npix
            xv = np.arange(xl[0], xl[1] + dxy, dxy)
            yv = np.arange(yl[0], yl[1], dxy)
            background_topography_dataset = app.gui.getvar("view_settings", "topography_dataset")
            dataset_list = [{"name": background_topography_dataset, "zmin": -99999.9, "zmax": 99999.9}]

            try:
                # Add wait box
                z = app.bathymetry_database.get_bathymetry_on_grid(xv, yv, CRS(3857), dataset_list,
                                                                   method=interp_method,
                                                                   waitbox=app.gui.window.dialog_wait)

                app.map.layer["main"].layer["background_topography"].opacity = opacity

                app.map.layer["main"].layer["background_topography"].color_scale_auto = autoscaling
                app.map.layer["main"].layer["background_topography"].color_scale_symmetric = True
                app.map.layer["main"].layer["background_topography"].color_scale_symmetric_side = "min"
                app.map.layer["main"].layer["background_topography"].color_scale_cmin = zmin
                app.map.layer["main"].layer["background_topography"].color_scale_cmax = zmax
                app.map.layer["main"].layer["background_topography"].hillshading = hillshading
                app.map.layer["main"].layer["background_topography"].color_map = colormap

                # color_values = []
                # color_values.append(
                #     {"color": "lightgreen", "lower_value": -1000.0, "upper_value": -500.0}
                # )
                # color_values.append(
                #     {"color": "yellow", "lower_value": -500.0, "upper_value": 0.0}
                # )
                # color_values.append(
                #     {"color": "#FFA500", "lower_value": 0.0, "upper_value": 500.0}
                # )
                # color_values.append({"color": "red", "lower_value": 500.0, "text": "VERY HIGH!"})
                # app.map.layer["main"].layer["background_topography"].color_values = color_values

                # data["x"] = xv
                # data["y"] = yv
                # data["z"] = z
                # data["crs"] = CRS(3857)

                # Now make an xarray DataArray with the data
                da = xr.DataArray(z, dims=["y", "x"], coords={"y": yv, "x": xv})
                da = da.rio.write_crs("EPSG:3857")
                app.background_topography = da
                # app.background_topography.attrs["crs"] = "EPSG:3857"

            except:
                print("Error loading background topo ...")
                traceback.print_exc()

                print("Updating background topography done.")

    except:
        print("Error updating background topo ...")
        traceback.print_exc()

    return da

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
    else:
        crstp = " (projected) - " + app.crs.to_string()
    app.gui.window.statusbar.set_text("crs_name", "   " + app.crs.name + crstp)
