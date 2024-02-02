from delftdashboard.app import app
from delftdashboard.toolboxes.observation_stations import observation_stations

def map_ready(mpbox):
    """MapBox callback function for when the map is ready.

    Parameters
    ----------
    mpbox : mplleaflet.Map
        Map object.
    """

    id = "observation_stations"

    # Add widget and read data
    mp = app.gui.popup_window[id].find_element_by_id("observation_stations_map").widget

    # Get popup data
    data = app.gui.popup_data[id]

    # Move to same map center as for general GUI
    if "map_center" in data:
        mp.jump_to(data["map_center"][0], data["map_center"][1], data["map_center"][2])

    # initialize toolbox
    data["toolbox"] = observation_stations.Toolbox("observation_stations", mapbox=mp)

    # Add layers to the mao 
    data["toolbox"].add_layers()
    data["toolbox"].select_tab()

    # Update list
    app.gui.popup_window[id].update()

def map_moved(coords, mpbox):
    """MapBox callback function for when the map is moved.

    Parameters
    ----------
    coords : tuple
        Coordinates of the map center.
    mpbox : mplleaflet.Map
        Map object.
    """
    pass

def select_source(*args):
    id = "observation_stations"
    data = app.gui.popup_data[id]

    index= app.gui.getvar("observation_stations", "active_source_index")
    data["toolbox"].select_source(index=index)

def select_station(*args):
    id = "observation_stations"
    data = app.gui.popup_data[id]

    data["toolbox"].select_station_from_list()

def select_naming_option(*args):
    id = "observation_stations"
    data = app.gui.popup_data[id]

    data["toolbox"].select_naming_option()

def add_stations_to_model(*args):
    id = "observation_stations"
    data = app.gui.popup_data[id]

    data["toolbox"].add_stations_to_model(model_option=data["option"])

def add_all_stations_to_model(*args):
    id = "observation_stations"
    data = app.gui.popup_data[id]

    data["toolbox"].add_all_stations_to_model(model_option=data["option"])    