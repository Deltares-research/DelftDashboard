from delftdashboard.app import app
from delftdashboard.operations import map
import geopandas as gpd
import time


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer:
        app.map.layer["modelmaker_fiat"].layer[active_layer].set_mode("active")


def draw_boundary(*args):
    selected_method = app.gui.getvar("modelmaker_fiat", "selected_aoi_method")
    if selected_method == "polygon":
        draw_polygon()
    elif selected_method == "box":
        draw_bbox()
    elif selected_method == "sfincs":
        print("Not yet implemented")
        pass
    elif selected_method == "file":
        load_aoi_file()


def zoom_to_boundary(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer:
        gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()

        # get the aoi bounds
        bounds = gdf.geometry.bounds

        # Fly to the site
        app.map.fit_bounds(bounds.minx[0], bounds.miny[0], bounds.maxx[0], bounds.maxy[0])
    else:
        app.gui.window.dialog_info(text="Please first select a model boundary.", title="No model boundary selected")


def generate_boundary(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer == "":
        app.gui.window.dialog_info(text="Please first select a model boundary.", title="No model boundary selected")
        return

    if app.model["fiat"].domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        
        # Initiate a new FIAT model
        app.model["fiat"].new()

    gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()
    gdf.to_file(
        app.model["fiat"].domain.database.drive / "aoi.geojson", driver="GeoJSON"
    )

    app.model["fiat"].domain.exposure_vm.create_interest_area(
        fpath=str(app.model["fiat"].domain.database.drive / "aoi.geojson")
    )

    app.map.layer["modelmaker_fiat"].layer[active_layer].hide()
    time.sleep(0.5)
    app.map.layer["modelmaker_fiat"].layer[active_layer].show()


def select_method(*args):
    app.gui.setvar("modelmaker_fiat", "selected_aoi_method", args[0])


def set_crs(*args):
    app.toolbox["modelmaker_fiat"].set_crs()


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


def draw_bbox():
    clear_aoi_layers()

    # Clear grid outline layer
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_bbox"
    )


def draw_polygon():
    clear_aoi_layers()

    # Set the crs of the polygon layer and draw it
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].draw()
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_polygon"
    )


def load_aoi_file():
    clear_aoi_layers()

    fname = app.gui.window.dialog_open_file(
        "Select Area of Interest File", filter="*.shp *.geojson *.gpkg"
    )
    if fname[0]:
        gdf = gpd.read_file(fname[0])

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
        layer.set_data(gdf)
        app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
        app.gui.setvar(
            "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_file"
        )

        # Fly to the site
        zoom_to_boundary()


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
