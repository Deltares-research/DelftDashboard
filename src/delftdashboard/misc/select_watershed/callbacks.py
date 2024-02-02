import numpy as np
import geopandas as gpd
import shapely

from delftdashboard.app import app

def open():
    pass

def map_ready(*args):
    """Adds a watershed (polygon) selector in the map"""
    mp = app.gui.popup_window["watershed"].find_element_by_id("watershed_map").widget
    layer = mp.add_layer("watersheds")
    polygon_layer = layer.add_layer(
        "watersheds",
        type="polygon_selector",
        line_color="k",
        line_width=1,
        fill_color="r",
        fill_opacity=0.6,
        select=select_watershed, # callback method for when user clicks on a polygon
        selection_type="multiple", 
        hover_property="name",
    )
    gdf = app.active_model.domain.data_catalog.get_geodataframe("watersheds")
    polygon_layer.set_data(gdf)
    bounds = gdf.geometry.total_bounds
    mp.fly_to((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2, 8)

def map_moved(*args):
    pass

def select_watershed(feature, widget):
    """Callback method for when the user clicks on a watershed. It updates the popup window data to the selected watersheds"""
    if not isinstance(feature, list):
        feature = [feature]
    app.gui.popup_data["watershed"] = feature
