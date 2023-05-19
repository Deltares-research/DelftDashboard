import numpy as np
import geopandas as gpd
import shapely

from delftdashboard.app import app as app

def open():
    pass

def map_ready():

    mp = app.gui.popup_window.find_element_by_id("track_selector_map").widget
    mp.jump_to(0.0, 0.0, 1)
    data = app.gui.popup_data
    # Container layers
    data["main_layer"] = mp.add_layer("track_selector")
    # Tracks layers
    data["track_layer"] = data["main_layer"].add_layer("tracks",
                                                       type="line_selector",
                                                       file_name="tracks.geojson",
                                                       select=select_track,
                                                       selection_type="single",
                                                       line_color="dodgerblue",
                                                       line_width=2,
                                                       line_color_selected="red",
                                                       line_width_selected=3,
                                                       hover_param="description")
    
    # Update data in tracks layer
    update_tracks()

def update_tracks():

    data = app.gui.popup_data

    tdb = data["track_database"]
    tracks_layer = data["track_layer"]
    lon = data["lon"]
    lat = data["lat"]

    # Get filter data
    distance = app.gui.getvar("cyclone_track_selector", "distance")
    year_min = app.gui.getvar("cyclone_track_selector", "year0")
    year_max = app.gui.getvar("cyclone_track_selector", "year1")

    # Get indices based on filter
    index = tdb.filter(lon=lon,
                       lat=lat,
                       distance=distance,
                       year_min=year_min,
                       year_max=year_max
                       )   

    # Get GeoDataFrame of tracks
    gdf = tdb.to_gdf(index=index)

    tracks_layer.set_data(gdf, 0)


def map_moved(coords):
    pass

def select_track(feature):
    app.gui.popup_data["database_index"] = feature["properties"]["database_index"]

def edit_filter(*args):
    update_tracks()
