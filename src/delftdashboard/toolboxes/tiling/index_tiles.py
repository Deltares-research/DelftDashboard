# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import geopandas as gpd
from delftdashboard.app import app
from delftdashboard.operations import map
# from cht_tiling.indices import make_index_tiles
from cht_tiling import TiledWebMap

# Callbacks

def select(*args):
    # De-activate() existing layers
    map.update()

def generate_index_tiles(*args):

    # Check what sort of model this is
    model = app.active_model

    if model.name == "sfincs_cht":
    
        dlg = app.gui.window.dialog_wait("Generating index tiles ...")
    
        grid = model.domain.grid.data
        path = "./tiles/indices"
        max_zoom = app.gui.getvar("tiling", "max_zoom")
        zoom_range = [0, max_zoom]

        # Create index tiles
        twmi = TiledWebMap(path, "indices", parameter="index")
        twmi.generate_index_tiles(grid,
                                  zoom_range,
                                  webviewer=True)

        # make_index_tiles(grid, path, zoom_range=zoom_range, format="png", webviewer=True)
        dlg.close()

    elif model.name == "hurrywave":

        dlg = app.gui.window.dialog_wait("Generating index tiles ...")
    
        grid = model.domain.grid.xugrid
        path = "./tiles/indices"
        max_zoom = app.gui.getvar("tiling", "max_zoom")
        zoom_range = [0, max_zoom]

        # Create index tiles
        twmi = TiledWebMap(path, "indices", parameter="index")
        twmi.generate_index_tiles(grid,
                                  zoom_range,
                                  webviewer=True)

        dlg.close()

    else:        
        app.gui.window.dialog_message(f"Tiling not supported for {model.name}")


def edit_variables(*args):
    pass