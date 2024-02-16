from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils
import geopandas as gpd
import os


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the mask include and exclude polygons
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_init"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["sfincs_hmt"].layer["mask"].activate()


def delete_mask_init_polygon(*args):
    """"Delete the initial mask polygon"""

    if len(app.toolbox["modelmaker_sfincs_hmt"].mask_init_polygon) == 0:
        return

    # Remove the filename
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_init_fname", "")

    # Remove from the map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_init"].clear()
    
    # Remove from the modelmaker
    app.toolbox["modelmaker_sfincs_hmt"].mask_init_polygon = gpd.GeoDataFrame()

    update()

def load_mask_init_polygon(*args):
    """Load the initial mask polygon"""

    fname = app.gui.window.dialog_open_file(
        "Select polygon file to initiliaze active mask with",
        filter="*.pol *.shp *.geojson",
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        gdf = gdf.to_crs(app.crs)

        # Store filename of the polygon
        app.gui.setvar("modelmaker_sfincs_hmt", "mask_init_fname", fname[0])

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_init"]
        layer.set_data(gdf)

        mask_init_polygon_created(gdf, 0, 0)

def mask_init_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_init_polygon = gdf
    update()


def mask_init_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_init_polygon = gdf


def draw_include_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].draw()


def delete_include_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "mask_include_polygon_index")
    # or: iac = args[0]
    feature_id = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].gdf.loc[
        index, "id"
    ]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].delete_feature(
        feature_id
    )

    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].mask_include_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "mask_include_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon) - 1,
        )
    
    # update list and GUI
    update()

def load_include_polygon(*args):
    fname = app.gui.window.dialog_open_file(
        "Select polygon file to include in active mask",
        filter="*.pol *.shp *.geojson",
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        gdf = gdf.to_crs(app.crs)

        nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon)
        # if already a polygon is present, add the new polygon to the existing one	
        if nrp > 0:
            gdf = app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon.append(gdf)
            gdf = gdf.reset_index(drop=True)

        include_polygon_created(gdf, 0, 0)


def save_include_polygon(*args):
    pass


def select_include_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon.loc[
        index, "id"
    ]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"].activate_feature(
        feature_id
    )

def include_polygon_created(gdf, index, id):
    """Add an include polygon to the modelmaker toolbox"""
   
    app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon = gdf

    # Add the polygon to the map
    layer = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_include"]
    layer.set_data(gdf)

    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_include_polygon_index", nrp - 1)
    update()


def include_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon = gdf


def include_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_include_polygon_index", index)
    update()


def draw_exclude_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].draw()


def delete_exclude_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index")
    # or: iac = args[0]
    feature_id = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].gdf.loc[
        index, "id"
    ]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].delete_feature(
        feature_id
    )
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].mask_exclude_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "mask_exclude_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon) - 1,
        )

    # update list and GUI
    update()


def load_exclude_polygon(*args):
    fname = app.gui.window.dialog_open_file(
        "Select polygon file to exclude from active mask",
        filter="*.pol *.shp *.geojson",
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        gdf = gdf.to_crs(app.crs)

        nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon)
        # if already a polygon is present, add the new polygon to the existing one	
        if nrp > 0:
            gdf = app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon.append(gdf)
            gdf = gdf.reset_index(drop=True)

        exclude_polygon_created(gdf, 0, 0)

def save_exclude_polygon(*args):
    pass

def select_exclude_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon.loc[
        index, "id"
    ]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"].activate_feature(
        feature_id
    )

def exclude_polygon_created(gdf, index, id):
    """Add an exclude polygon to the modelmaker toolbox"""
   
    app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon = gdf

    # Add the polygon to the map
    layer = app.map.layer["modelmaker_sfincs_hmt"].layer["mask_exclude"]
    layer.set_data(gdf)

    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index", nrp - 1)
    update()


def exclude_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon = gdf


def exclude_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_index", index)
    update()


def mask_add_tick_box(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_active_add", args[0])


def mask_del_tick_box(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_active_del", args[0])


def tick_box(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_active_reset", args[0])


def edit_mask_active(*args):
    toolbox_name = "modelmaker_sfincs_hmt"
    path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
    pop_win_config_path = os.path.join(path, "edit_mask_active.yml")
    okay, data = app.gui.popup(pop_win_config_path, None)
    if not okay:
        return
    else:
        update_mask_active()

def update():
    """Update the lists with the include and exclude polygons in the modelmaker"""

    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon)
    incnames = []
    for index in range(len(app.toolbox["modelmaker_sfincs_hmt"].mask_include_polygon)):
        # create a name with %02d format
        incnames.append("Polygon " + "%02d" % (index+1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_mask_include_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_include_polygon_names", incnames)

    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon)
    excnames = []
    for index in range(len(app.toolbox["modelmaker_sfincs_hmt"].mask_exclude_polygon)):
        # create a name with %02d format
        excnames.append("Polygon " + "%02d" % (index+1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_mask_exclude_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "mask_exclude_polygon_names", excnames)

    app.gui.window.update()


def update_mask_active(*args):
    app.toolbox["modelmaker_sfincs_hmt"].update_mask_active()
