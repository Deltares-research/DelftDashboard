# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
# import geopandas as gpd
import os

from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks
def select(*args):
    # De-activate() existing layers
    map.update()
    # Tab selected
    app.toolbox["flood_map"].set_layer_mode("active")

def load_topobathy_geotiff(*args):
    # Load topobathy geotiff
    app.toolbox["flood_map"].load_topobathy_geotiff()
    # Now set the text in the label (File : and file name without path)
    fname = os.path.basename(app.toolbox["flood_map"].topobathy_geotiff)
    app.gui.setvar("flood_map", "topo_file_string", "File : " + fname)

def load_index_geotiff(*args):
    # Load index geotiff
    app.toolbox["flood_map"].load_index_geotiff()
    # Now set the text in the label (File : and file name without path)
    fname = os.path.basename(app.toolbox["flood_map"].index_geotiff)
    app.gui.setvar("flood_map", "index_file_string", "File : " + fname)

def load_map_output(*args):
    # Load map output
    app.toolbox["flood_map"].load_map_output()
    fname = os.path.basename(app.toolbox["flood_map"].map_file_name)
    app.gui.setvar("flood_map", "map_file_string", "File : " + fname)

def edit_table(*args):
    pass
