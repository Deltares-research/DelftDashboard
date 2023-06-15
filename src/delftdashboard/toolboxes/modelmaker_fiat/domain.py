from delftdashboard.app import app
from delftdashboard.operations import map
from hydromt_fiat.api.view_model import HydroMtViewModel
import geopandas as gpd


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["fiat"].layer["grid"].set_mode("active")
    app.map.layer["modelmaker_fiat"].layer["area_of_interest"].set_mode("active")


def select_method(*args):
    app.gui.setvar("modelmaker_fiat", "selected_aoi_method", args[0])


def clear_aoi_layers():
    aoi_layers = [
        "area_of_interest_bbox",
        "area_of_interest_polygon",
        "area_of_interest_from_file",
        "area_of_interest_from_sfincs",
    ]
    if app.gui.getvar("modelmaker_fiat", "area_of_interest") == 1:
        for l in aoi_layers:
            layer = app.map.layer["modelmaker_fiat"].layer[l]
            layer.clear()


def draw_bbox(*args):
    clear_aoi_layers()

    # Clear grid outline layer
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_bbox"
    )


def draw_polygon(*args):
    clear_aoi_layers()

    # Set the crs of the polygon layer and draw it
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_polygon"
    )


def load_aoi_file(*args):
    clear_aoi_layers()

    fname = app.gui.window.dialog_open_file(
        "Select Area of Interest File", filter="*.shp *.geojson *.gpkg"
    )
    if fname[0]:
        gdf = gpd.read_file(fname[0])

        # get the center of the polygon
        x0 = gdf.geometry.centroid.x[0]
        y0 = gdf.geometry.centroid.y[0]

        # Fly to the site
        app.map.fly_to(x0, y0, 7)

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
        layer.add_feature(gdf)
        app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
        app.gui.setvar(
            "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_file"
        )


def load_sfincs_domain(*args):
    clear_aoi_layers()

    group = "sfincs_hmt"
    lenx = app.gui.getvar(group, "dx") * app.gui.getvar(group, "mmax")
    leny = app.gui.getvar(group, "dy") * app.gui.getvar(group, "nmax")

    app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_sfincs"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer[
        "area_of_interest_from_sfincs"
    ].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        lenx,
        leny,
        app.gui.getvar(group, "rotation"),
    )
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_sfincs"
    )


def fly_to_site(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()

    # get the aoi bounds
    bounds = gdf.geometry.bounds

    # Fly to the site
    app.map.fit_bounds(bounds.minx[0], bounds.miny[0], bounds.maxx[0], bounds.maxy[0])


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


def generate_aoi(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer:
        gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()

        hydro_vm = HydroMtViewModel(
            app.config["working_directory"], app.config["data_libs_fiat"][0]
        )
        gdf.to_file(HydroMtViewModel.database.drive / "aoi.geojson", driver="GeoJSON")
        hydro_vm.exposure_vm.create_interest_area(
            filepath=str(HydroMtViewModel.database.drive / "aoi.geojson")
        )
