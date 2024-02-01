import numpy as np
import geopandas as gpd
import shapely

from delftdashboard.app import app

def open():
    pass

def map_ready(*args):
    mp = app.gui.popup_window["watershed"].find_element_by_id("watershed_map").widget
    mp.jump_to(0.0, 0.0, 0)
    layer = mp.add_layer("watersheds")
    polygon_layer = layer.add_layer(
        "aggr_layer",
        type="polygon_selector",
        line_color="k",
        line_width=1,
        fill_color="r",
        fill_opacity=0.6,
        select=select_watershed,
        hover_property="",
    )
    polygon_layer.set_data(gdf, 0)

def map_moved(*args):
    pass

def select_watershed(feature, widget):
    app.gui.popup_data["watershed"] = feature["properties"]
