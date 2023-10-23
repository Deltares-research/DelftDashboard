import numpy as np
import math
import os

from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils
import time

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].activate()


def select_method(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "setup_grid_methods_index", args[0])


def draw_bbox(*args):
    group = "modelmaker_sfincs_hmt"

    app.map.layer[group].layer["grid_outline"].crs = app.crs
    app.map.layer[group].layer["grid_outline"].draw()

def draw_aio(*args):
    group = "modelmaker_sfincs_hmt"

    app.map.layer[group].layer["area_of_interest"].crs = app.crs
    app.map.layer[group].layer["area_of_interest"].draw()



def load_aio(*args):
    fname = app.gui.window.dialog_open_file(
        "Select polygon file", filter="*.pol *.shp *.geojson"
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        # get the center of the polygon
        lon = gdf.to_crs(4326).geometry.centroid.x[0]
        lat = gdf.to_crs(4326).geometry.centroid.y[0]

        # Fly to the site
        app.map.fly_to(lon, lat, 7)

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"]
        layer.set_data(gdf)

        aio_created(gdf.to_crs(app.crs), 0, 0)

        if not app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].gdf.empty:
            app.gui.setvar("modelmaker_sfincs_hmt", "grid_outline", 1)


def fly_to_site(*args):
    gdf = app.toolbox["modelmaker_sfincs_hmt"].grid_outline
    # get the center of the polygon
    lon = gdf.to_crs(4326).geometry.centroid.x[0]
    lat = gdf.to_crs(4326).geometry.centroid.y[0]

    # specify a logical zoom level based on the extent of the bbox to make it fit in the window
    bbox = gdf.to_crs(4326).geometry.total_bounds
    dx = bbox[2] - bbox[0]
    dy = bbox[3] - bbox[1]

    zoom = 15 - math.log(max(dx, dy), 2)

    # Fly to the site'
    app.map.fly_to(lon, lat, zoom)


def grid_outline_created(gdf, index, id):
    group = "modelmaker_sfincs_hmt"
    if len(gdf) > 1:
        # Only keep the latest grid outline
        id0 = gdf["id"][0]
        app.map.layer[group].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index(drop=True)
    app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf

    # check if bbox is defined
    if not gdf.empty:
        app.gui.setvar(group, "grid_outline", 1)

    # Remove area of interest (if present)
    if not app.map.layer[group].layer["area_of_interest"].gdf.empty:
        app.map.layer[group].layer["area_of_interest"].clear()
    
    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def aio_created(gdf, index, id):
    group = "modelmaker_sfincs_hmt"
    if len(gdf) > 1:
        # Remove the old area of interest
        id0 = gdf["id"][0]
        app.map.layer[group].layer["area_of_interest"].delete_feature(
            id0
        )
        gdf = gdf.drop([0]).reset_index(drop=True)
    app.toolbox[group].area_of_interest = gdf

    # Get grid resolution
    dx = app.gui.getvar(group, "dx")
    dy = app.gui.getvar(group, "dy")
    res = np.mean([dx, dy])

    # Create grid outline
    if app.crs.is_geographic:
        precision = 6
    else:
        precision = 3

    x0, y0, mmax, nmax, rot = utils.rotated_grid(
        gdf.unary_union, res, dec_origin=precision
    )
    app.gui.setvar(group, "x0", round(x0, precision))
    app.gui.setvar(group, "y0", round(y0, precision))
    app.gui.setvar(group, "mmax", mmax)
    app.gui.setvar(group, "nmax", nmax)
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )    
    app.gui.setvar(group, "rotation", round(rot, 3))
    redraw_rectangle()

    app.gui.window.update()


def aio_modified(gdf, index, id):
    group = "modelmaker_sfincs_hmt"
    app.toolbox[group].area_of_interest = gdf

    # Get grid resolution
    dx = app.gui.getvar(group, "dx")
    dy = app.gui.getvar(group, "dy")
    res = np.mean([dx, dy])

    # Create grid outline
    if app.crs.is_geographic:
        precision = 6
    else:
        precision = 3

    x0, y0, mmax, nmax, rot = utils.rotated_grid(
        gdf.unary_union, res, dec_origin=precision
    )
    app.gui.setvar(group, "x0", round(x0, precision))
    app.gui.setvar(group, "y0", round(y0, precision))
    app.gui.setvar(group, "mmax", mmax)
    app.gui.setvar(group, "nmax", nmax)
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )
    app.gui.setvar(group, "rotation", round(rot, 3))
    redraw_rectangle()
    app.gui.window.update()


def generate_grid(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_grid()


def update_geometry():
    group = "modelmaker_sfincs_hmt"
    gdf = app.toolbox[group].grid_outline

    if app.crs.is_geographic:
        precision = 6
    else:
        precision = 3

    app.gui.setvar(group, "x0", round(gdf["x0"][0], precision))
    app.gui.setvar(group, "y0", round(gdf["y0"][0], precision))
    lenx = gdf["dx"][0]
    leny = gdf["dy"][0]
    app.toolbox[group].lenx = lenx
    app.toolbox[group].leny = leny
    app.gui.setvar(group, "rotation", round(gdf["rotation"][0] * 180 / math.pi, 1))
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )

def edit_origin(*args):
    redraw_rectangle()


def edit_nmmax(*args):
    redraw_rectangle()


def edit_rotation(*args):
    redraw_rectangle()


def edit_dxdy(*args):
    group = "modelmaker_sfincs_hmt"
    lenx = app.toolbox[group].lenx
    leny = app.toolbox[group].leny
    app.gui.setvar(
        group, "nmax", np.floor(leny / app.gui.getvar(group, "dy")).astype(int)
    )
    app.gui.setvar(
        group, "mmax", np.floor(lenx / app.gui.getvar(group, "dx")).astype(int)
    )
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )

def edit_res(*args):
    group = "modelmaker_sfincs_hmt"
    
    # set dx and dy to res
    app.gui.setvar(group, "dx", app.gui.getvar(group, "res"))
    app.gui.setvar(group, "dy", app.gui.getvar(group, "res"))

    edit_dxdy(*args)

def edit_domain(*args):
    toolbox_name = "modelmaker_sfincs_hmt"
    path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
    pop_win_config_path  = os.path.join(path, "edit_domain.yml")
    okay, data = app.gui.popup(pop_win_config_path , None)
    if not okay:
        return

def redraw_rectangle():
    group = "modelmaker_sfincs_hmt"
    app.toolbox[group].lenx = app.gui.getvar(
        group, "dx"
    ) * app.gui.getvar(group, "mmax")
    app.toolbox[group].leny = app.gui.getvar(
        group, "dy"
    ) * app.gui.getvar(group, "nmax")
    app.map.layer[group].layer["grid_outline"].clear()
    app.map.layer[group].layer["grid_outline"].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        app.toolbox[group].lenx,
        app.toolbox[group].leny,
        app.gui.getvar(group, "rotation"),
    )

    # pause the code for 5 seconds to allow the map to update
    time.sleep(5)

    gdf = app.map.layer[group].layer["grid_outline"].get_gdf()
    app.toolbox[group].grid_outline = gdf
    # if not app.toolbox[group].grid_outline.empty:
    #NOTE apparently this needs time to update the map hence first time the gdf is empty
    # howeevr, the bbox should be present once reaching this part of the code
    app.gui.setvar(group, "grid_outline", 1)


def read_setup_yaml(*args):
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_hmt"].read_setup_yaml(fname[0])


def write_setup_yaml(*args):
    app.toolbox["modelmaker_sfincs_hmt"].write_setup_yaml()


def build(*args):
    app.toolbox["modelmaker_sfincs_hmt"].build()
