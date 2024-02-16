# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import numpy as np
import traceback
from pyproj import CRS

from delftdashboard.app import app
from cht.bathymetry.bathymetry_database import bathymetry_database
from cht.misc.geometry import RegularGrid

import geopandas as gpd
from shapely.geometry import box
import xarray as xr


def map_ready(*args):
    # This method is called when the map has been loaded
    print("Map is ready !")

    # Find map widget
    element = app.gui.window.find_element_by_id("map")
    app.map = element.widget

    # Add main DDB layer
    main_layer = app.map.add_layer("main")

    # Add background topography layer
    app.background_topography_layer = main_layer.add_layer(
        "background_topography", type="raster"
    )

    # Set update method for topography layer
    app.background_topography_layer.update = update_background

    # Go to point
    if "map_center" in app.config:
        lon, lat, zoom = app.config["map_center"]
        app.map.jump_to(lon, lat, zoom)

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

    if app.auto_update_topography and app.view["topography"]["visible"]:
        coords = app.map.map_extent
        xl = [coords[0][0], coords[1][0]]
        yl = [coords[0][1], coords[1][1]]
        wdt = app.map.view.geometry().width()
        if app.view["topography"]["quality"] == "high":
            npix = wdt
        elif app.view["topography"]["quality"] == "medium":
            npix = int(wdt * 0.5)
        else:
            npix = int(wdt * 0.25)

        dxy = (xl[1] - xl[0]) / npix
        xv = np.arange(xl[0], xl[1], dxy)
        yv = np.arange(yl[0], yl[1], dxy)

        # NOTE : we first check if hydromt data is initiated, if not we use the ddb data
        if app.config["data_libs"] is not None:
            # we then check if the background topography is in the hydromt data catalog
            if app.background_topography in app.data_catalog.keys:
                try:
                    # convert active window to geodataframe
                    bbox = box(min(xv), min(yv), max(xv), max(yv))
                    gdf = gpd.GeoDataFrame(geometry=[bbox], crs=CRS(4326))

                    # initilize empty xarray
                    da_dep = xr.DataArray(
                        np.float32(np.full([len(yv), len(xv)], np.nan)),
                        coords={"y": yv, "x": xv},
                        dims=["y", "x"],
                    )
                    da_dep.raster.set_crs(4326)

                    # get data from hydromt data catalog and reproject to active window
                    da = app.data_catalog.get_rasterdataset(
                        app.background_topography,
                        geom=gdf,
                        buffer=5,
                        zoom_level=(dxy, "degree"),
                    )
                    da = da.raster.reproject_like(da_dep, method="bilinear").load()
                    da.raster.set_nodata(np.nan)

                    # set data to background topography layer
                    app.background_topography_layer.set_data(
                        x=xv,
                        y=yv,
                        z=da.values,
                        colormap=app.color_map_earth,
                        decimals=0,
                    )
                except:
                    print("Error loading hydromt background topo ...")
            # TODO: FdG; I suggest to remove the part below as we're not going to use this data
            elif app.config["bathymetry_database"] is not None:
                try:
                    dataset = bathymetry_database.get_dataset(app.background_topography)
                    dataset_list = [
                        {"dataset": dataset, "zmin": -99999.9, "zmax": 99999.9}
                    ]
                    z = bathymetry_database.get_bathymetry_on_grid(
                        xv,
                        yv,
                        CRS(4326),
                        dataset_list,
                        method=app.view["topography"]["interp_method"],
                    )
                    app.background_topography_layer.set_data(
                        x=xv, y=yv, z=z, colormap=app.color_map_earth, decimals=0
                    )
                except:
                    print("Error loading ddb background topo ...")


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
    try:
        assert app.map
        app.map.set_mouse_default()
    except AttributeError:
        pass
