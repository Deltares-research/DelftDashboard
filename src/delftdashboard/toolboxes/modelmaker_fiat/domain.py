from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["fiat"].layer["grid"].set_mode("active")
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].set_mode("active")


def select_method(*args):
    app.gui.setvar("modelmaker_fiat", "selected_aoi_method", args[0])


def draw_bbox(*args):
    # Clear grid outline layer
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)

    # Remove the area of interest
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].clear()


def draw_aio(*args):
    # Clear grid outline layer
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)


def fly_to_site(*args):
    gdf = app.toolbox["modelmaker_fiat"].area_of_interest
    # get the center of the polygon
    x0 = gdf.geometry.centroid.x[0]
    y0 = gdf.geometry.centroid.y[0]

    # Fly to the site
    app.map.fly_to(x0, y0, 7)


def read_setup_yaml(*args):
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox["modelmaker_fiat"].read_setup_yaml(fname[0])


def write_setup_yaml(*args):
    app.toolbox["modelmaker_fiat"].write_setup_yaml()
    app.toolbox["modelmaker_fiat"].write_include_polygon()
    app.toolbox["modelmaker_fiat"].write_exclude_polygon()
    app.toolbox["modelmaker_fiat"].write_boundary_polygon()


def build_model(*args):
    app.toolbox["modelmaker_fiat"].build_model()


def load_sfincs_domain(*args):
    NotImplemented


def load_aoi_file(*args):
    fname = app.gui.window.dialog_open_file(
        "Select Area of Interest File", filter="*.shp *.geojson *.gpkg"
    )
    if fname[0]:
        app.toolbox["modelmaker_fiat"].load_aoi_file(fname[0])

        # get the center of the polygon
        x0 = gdf.geometry.centroid.x[0]
        y0 = gdf.geometry.centroid.y[0]

        # Fly to the site
        app.map.fly_to(x0, y0, 7)

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest"]
        layer.clear()
        layer.add_feature(gdf)
        app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)


def generate_aoi(*args):
    app.toolbox["modelmaker_fiat"].generate_aoi()
