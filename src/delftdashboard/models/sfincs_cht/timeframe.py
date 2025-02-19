# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers


    # from geopandas import GeoDataFrame
    # from shapely.geometry import Point
    # gdf = GeoDataFrame(geometry=[Point(0, 0)], crs=4326)
    # # Add a url property to the geodataframe
    # url_list = ["https://www.google.com"]
    # des_list = ["Description"]
    # gdf["url"] = url_list
    # gdf["description"] = des_list
    # gdf["icon_url"] = "tide_icon_48x48.png"
    # app.map.layer["sfincs_cht"].layer["obs_points"].set_data(gdf)

    map.update()


def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()

    # Now check that the boundary and other forcing fully covers the simulation time
    app.model["sfincs_cht"].check_times()
