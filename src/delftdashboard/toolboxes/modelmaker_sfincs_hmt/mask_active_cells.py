# -*- coding: utf-8 -*-
"""
GUI methods for modelmaker_sfincs_hmt -> mask_active_cells

Created on Mon May 10 12:18:09 2021

@author: Maarten van Ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_polygon"].set_mode("active")
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].set_mode("active")
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].set_mode("active")
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_active"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_mode("active")


def select_mask_polygon_method(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_polygon_methods_index", args[0])


def draw_mask_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_polygon"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_polygon"].draw()


def delete_mask_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].mask_polygon) == 0:
        return
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_polygon"].clear()
    # Delete from app
    gdf = app.toolbox["modelmaker_sfincs_hmt"].mask_polygon
    app.toolbox["modelmaker_sfincs_hmt"].mask_polygon = gdf.drop(
        gdf.index, inplace=True
    )
    update()


def load_mask_polygon(*args):
    fname = app.gui.window.dialog_open_file(
        "Select polygon file", filter="*.pol *.shp *.geojson"
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        gdf = gdf.to_crs(4326)

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_polygon"]
        layer.clear()
        layer.add_feature(gdf)

        mask_polygon_created(gdf, 0, 0)


def save_mask_polygon(*args):
    pass


def mask_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_polygon = gdf
    update()


def mask_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_polygon = gdf


def draw_include_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].draw()


def delete_include_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "mask_include_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].include_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].delete_feature(
        feature_id
    )
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].include_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].include_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].include_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "mask_include_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].include_polygon) - 1,
        )
    update()


def load_include_polygon(*args):
    pass


def save_include_polygon(*args):
    pass


def select_include_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].include_polygon.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].activate_feature(
        feature_id
    )


def include_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].include_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_include_polygon_index", nrp - 1)
    update()


def include_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].include_polygon = gdf


def include_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_include_polygon_index", index)
    update()


def draw_exclude_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].draw()


def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon.loc[index, "id"]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].delete_feature(
        feature_id
    )
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].exclude_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "mask_exclude_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon) - 1,
        )
    update()


def load_exclude_polygon(*args):
    pass


def save_exclude_polygon(*args):
    pass


def select_exclude_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon.loc[index, "id"]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].activate_feature(
        feature_id
    )


def exclude_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index", nrp - 1)
    update()


def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon = gdf


def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index", index)
    update()


def tick_box(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_active_reset", args[0])


def update():
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_include_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "include_polygon_names", incnames)

    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].exclude_polygon)
    excnames = []
    for ip in range(nrp):
        excnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_exclude_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "exclude_polygon_names", excnames)

    app.gui.window.update()


def update_mask_active(*args):
    app.toolbox["modelmaker_sfincs_hmt"].update_mask_active()
