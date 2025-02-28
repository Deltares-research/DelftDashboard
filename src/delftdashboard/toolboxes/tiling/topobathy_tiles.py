# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import geopandas as gpd
import os
from delftdashboard.app import app
from delftdashboard.operations import map
# from cht_tiling.topobathy import make_topobathy_tiles
from cht_tiling import TiledWebMap

# Callbacks
def select(*args):
    # De-activate() existing layers
    map.update()

def generate_topobathy_tiles(*args):
    # Check what sort of model this is
    model = app.active_model
    index_path = "./tiles/indices"
    path = "./tiles/topobathy"

    # First check of index tiles exist
    if not os.path.exists(index_path):
        app.gui.window.dialog_message("Please generate index tiles first !")
        return

    if model.name == "sfincs_cht":
    
        dlg = app.gui.window.dialog_wait("Generating topo/bathy tiles ...")

        dem_list = app.toolbox["modelmaker_sfincs_cht"].selected_bathymetry_datasets
        # Loop through dem_list (now only using twm)
        for dem in dem_list:
            dem["twm"] = app.bathymetry_database.get_dataset(dem["name"]).data

        # data_list = []

        # # Getting tiles directly from tiled web map
        # data_path = r"c:\work\delftdashboard\data\bathymetry\ph_dtm_leyte_samar"
        # twm_data = TiledWebMap(data_path, "topobathy", parameter="elevation")
        # data_list.append({"twm": twm_data, "zmin": 0.1})

        # Create topo bathy tiles
        twmb = TiledWebMap(path, "topobathy", parameter="elevation")
        twmb.generate_topobathy_tiles(dem_list,
                                      index_path=index_path,
                                      write_metadata=False,
                                      parallel=False
                                     )

        # make_topobathy_tiles(path,
        #                     dem_list=dem_list,
        #                     bathymetry_database=app.bathymetry_database,
        #                     index_path=index_path,
        #                     zoom_range=zoom_range,
        #                     quiet=False,
        #                     make_webviewer=True,
        #                     write_metadata=False,    
        #                     make_availability_file=False,
        #                     make_lower_levels=True,
        #                     make_highest_level=True,
        #                     skip_existing=False,
        #                     interpolation_method="linear",
        #                     encoder="terrarium",
        #                     compress_level=6,
        # )

        dlg.close()

    elif model.name == "hurrywave":
        app.gui.window.dialog_message(f"Tiling not needed for {model.name} !")

    else:        
        app.gui.window.dialog_message(f"Tiling not supported for {model.name}")

def edit_variables(*args):
    pass