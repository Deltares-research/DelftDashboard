import numpy as np
import math

from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].set_mode("active")
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].set_mode("active")

def select_method(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "setup_grid_methods_index", args[0])

def draw_bbox(*args):
    # Clear grid outline layer
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].draw()
    app.gui.setvar("modelmaker_sfincs_hmt", "grid_outline", 1)

    # Remove the area of interest
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].clear()

def draw_aio(*args):
    # Clear grid outline layer
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].draw()
    app.gui.setvar("modelmaker_sfincs_hmt", "grid_outline", 1)

def load_aio(*args):
    fname = app.gui.window.dialog_open_file("Select polygon file", filter="*.pol *.shp *.geojson")
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(
                feats=utils.read_geoms(fn=fname[0]), crs=app.crs
            )
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        gdf = gdf.to_crs(4326)

        # get the center of the polygon
        x0 = gdf.geometry.centroid.x[0]
        y0 = gdf.geometry.centroid.y[0]

        # Fly to the site
        app.map.fly_to(x0, y0, 7)

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"]
        layer.clear()
        layer.add_feature(gdf)
        app.gui.setvar("modelmaker_sfincs_hmt", "grid_outline", 1)
        
        aio_created(gdf,0,0)
        
def fly_to_site(*args):
    gdf = app.toolbox["modelmaker_sfincs_hmt"].grid_outline
    # get the center of the polygon
    x0 = gdf.geometry.centroid.x[0]
    y0 = gdf.geometry.centroid.y[0]

    # Fly to the site
    app.map.fly_to(x0, y0, 7)

def grid_outline_created(gdf, index, id):
    if len(gdf) > 1:
        # Remove the old grid outline
        id0 = gdf["id"][0]
        app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def aio_created(gdf, index, id):
    if len(gdf) > 1:
        # Remove the old area of interest
        id0 = gdf["id"][0]
        app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index()
    app.toolbox["modelmaker_sfincs_hmt"].area_of_interest = gdf

    # Get grid resolution
    dx = app.gui.getvar("modelmaker_sfincs_hmt", "dx")
    dy = app.gui.getvar("modelmaker_sfincs_hmt", "dy")
    res = np.mean([dx,dy])

    # Create grid outline
    x0, y0, mmax, nmax, rot = utils.rotated_grid(gdf.unary_union, res, dec_origin=6)
    app.gui.setvar("modelmaker_sfincs_hmt", "x0", round(x0,3))
    app.gui.setvar("modelmaker_sfincs_hmt", "y0", round(y0,3))
    app.gui.setvar("modelmaker_sfincs_hmt", "mmax", mmax)
    app.gui.setvar("modelmaker_sfincs_hmt", "nmax", nmax)
    app.gui.setvar("modelmaker_sfincs_hmt", "rotation", round(rot,3))
    redraw_rectangle()
    app.gui.window.update()
    

def aio_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].area_of_interest = gdf

    # Get grid resolution
    dx = app.gui.getvar("modelmaker_sfincs_hmt", "dx")
    dy = app.gui.getvar("modelmaker_sfincs_hmt", "dy")
    res = np.mean([dx,dy])

    # Create grid outline
    x0, y0, mmax, nmax, rot = utils.rotated_grid(gdf.unary_union, res, dec_origin=6)
    app.gui.setvar("modelmaker_sfincs_hmt", "x0", round(x0,3))
    app.gui.setvar("modelmaker_sfincs_hmt", "y0", round(y0,3))
    app.gui.setvar("modelmaker_sfincs_hmt", "mmax", mmax)
    app.gui.setvar("modelmaker_sfincs_hmt", "nmax", nmax)
    app.gui.setvar("modelmaker_sfincs_hmt", "rotation", round(rot,3))
    redraw_rectangle()
    app.gui.window.update()


def generate_grid(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_grid()


def update_geometry():
    gdf = app.toolbox["modelmaker_sfincs_hmt"].grid_outline
    group = "modelmaker_sfincs_hmt"
    app.gui.setvar(group, "x0", round(gdf["x0"][0], 3))
    app.gui.setvar(group, "y0", round(gdf["y0"][0], 3))
    lenx = gdf["dx"][0]
    leny = gdf["dy"][0]
    app.toolbox["modelmaker_sfincs_hmt"].lenx = lenx
    app.toolbox["modelmaker_sfincs_hmt"].leny = leny
    app.gui.setvar(group, "rotation", round(gdf["rotation"][0] * 180 / math.pi, 1))
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )


def edit_origin(*args):
    redraw_rectangle()


def edit_nmmax(*args):
    redraw_rectangle()


def edit_rotation(*args):
    redraw_rectangle()


def edit_dxdy(*args):
    group = "modelmaker_sfincs_hmt"
    lenx = app.toolbox["modelmaker_sfincs_hmt"].lenx
    leny = app.toolbox["modelmaker_sfincs_hmt"].leny
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )


def redraw_rectangle():
    group = "modelmaker_sfincs_hmt"
    app.toolbox["modelmaker_sfincs_hmt"].lenx = app.gui.getvar(
        group, "dx"
    ) * app.gui.getvar(group, "mmax")
    app.toolbox["modelmaker_sfincs_hmt"].leny = app.gui.getvar(
        group, "dy"
    ) * app.gui.getvar(group, "nmax")
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].clear()
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        app.toolbox["modelmaker_sfincs_hmt"].lenx,
        app.toolbox["modelmaker_sfincs_hmt"].leny,
        app.gui.getvar(group, "rotation"),
    )
    if app.toolbox["modelmaker_sfincs_hmt"].grid_outline.empty:
        gdf = app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].get_gdf()
        app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf

def read_setup_yaml(*args):
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox["modelmaker_hurrywave"].read_setup_yaml(fname[0])

def write_setup_yaml(*args):
    app.toolbox["modelmaker_hurrywave"].write_setup_yaml()
    app.toolbox["modelmaker_hurrywave"].write_include_polygon()
    app.toolbox["modelmaker_hurrywave"].write_exclude_polygon()
    app.toolbox["modelmaker_hurrywave"].write_boundary_polygon()

def build_model(*args):
    app.toolbox["modelmaker_hurrywave"].build_model()