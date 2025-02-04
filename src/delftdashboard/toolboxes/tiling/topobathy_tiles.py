# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import geopandas as gpd
from delftdashboard.app import app
from delftdashboard.operations import map
from cht_tiling.topobathy import make_topobathy_tiles

# Callbacks

def select(*args):
    # De-activate() existing layers
    map.update()

def generate_topobathy_tiles(*args):
    # Check what sort of model this is
    model = app.active_model
    index_path = "./tiles/indices"
    path = "./tiles/topobathy"
    max_zoom = app.gui.getvar("tiling", "max_zoom")
    zoom_range = [0, max_zoom]
    if model.name == "sfincs_cht":
        dem_list = app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets
    elif model.name == "hurrywave":
        dem_list = app.toolbox["modelmaker_hurrywave"].selected_bathymetry_datasets
    else:
        return

    make_topobathy_tiles(path,
                         dem_list=dem_list,
                         bathymetry_database=app.bathymetry_database,
                         index_path=index_path,
                         zoom_range=zoom_range,
                         quiet=False,
                         make_webviewer=True,
                         write_metadata=False,    
                         make_availability_file=False,
                         make_lower_levels=True,
                         make_highest_level=True,
                         skip_existing=False,
                         interpolation_method="linear",
                         encoder="terrarium",
                         compress_level=6,
    )

def edit_variables(*args):
    pass