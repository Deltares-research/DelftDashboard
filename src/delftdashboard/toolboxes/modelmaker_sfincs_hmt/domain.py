import numpy as np
import math
import os
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.menu import coordinate_system

from hydromt import gis_utils
from hydromt_sfincs import utils

def select(*args):
    """Callback to specify what happens when you select the domain tab"""
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["grid_outline"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["area_of_interest"].activate()

def select_model_type(*args):
    """" 
    Adjusts default GUI settings based on different model types:
    
    0: Overland
    1: Surge
    2: Quadtree (not implemented yet, just as example why this is handy)

    Parameters:
    *args: Additional arguments (not used in the function)

    """	

    # TODO: Make this into an enum, e.g.:
    # class ModelType(Enum):
    #     OVERLAND = 0
    #     SURGE = 1
    #     QUADTREE = 2 # Not implemented
    
    group = "modelmaker_sfincs_hmt"

    model_type = app.gui.getvar(group, "model_type_index")

    if model_type == 0:
        app.gui.setvar(group, "mask_active_zmax", 10.0)
        app.gui.setvar(group, "mask_active_zmin", -10.0)
        app.gui.setvar(group, "mask_active_drop_area", 10.0)
        app.gui.setvar(group, "mask_active_fill_area", 10.0)
        app.gui.setvar(group, "auto_select_utm", True)
    elif model_type == 1:
        app.gui.setvar(group, "mask_active_zmax", 5.0)
        app.gui.setvar(group, "mask_active_zmin", -500.0)
        app.gui.setvar(group, "mask_active_drop_area", 10.0)
        app.gui.setvar(group, "mask_active_fill_area", 100.0)
        app.gui.setvar(group, "auto_select_utm", False)

def select_setup_grid_method(*args):
    """" Change default method for domain selection, given the type of forcing conditions you want to use"""
    group = "modelmaker_sfincs_hmt"

    include_precip =  app.gui.getvar(group, "include_precip")
    # include_rivers = app.gui.getvar(group, "include_rivers")
    # include_waves = app.gui.setvar(group, "include_waves", False)    

    watershed = False
    if include_precip: #or include_rivers:
        watershed = True

    if watershed:
        app.gui.setvar(group, "setup_grid_method", "Select Watershed")
    else:
        app.gui.setvar(group, "setup_grid_method", "Draw Bounding Box")

def draw_bbox(*args):
    """Callback to specify what happens when you click the draw bbox button"""

    group = "modelmaker_sfincs_hmt"

    app.map.layer[group].layer["grid_outline"].crs = app.crs
    app.map.layer[group].layer["grid_outline"].draw()

def draw_aio(*args):
    """Callback to specify what happens when you click the draw area of interest button"""
    group = "modelmaker_sfincs_hmt"

    app.map.layer[group].layer["area_of_interest"].crs = app.crs
    app.map.layer[group].layer["area_of_interest"].draw()

def load_aio(*args):
    """Callback to specify what happens when you click the load area of interest button"""
    group = "modelmaker_sfincs_hmt"

    # Load a polygon file
    fname = app.gui.window.dialog_open_file(
        "Select polygon file", filter="*.pol *.shp *.geojson"
    )
    if fname[0]:
        # for .pol files we assume that they are in the coordinate system of the current map
        if str(fname[0]).endswith(".pol"):
            gdf = utils.polygon2gdf(feats=utils.read_geoms(fn=fname[0]), crs=app.crs)
        else:
            gdf = app.model["sfincs_hmt"].domain.data_catalog.get_geodataframe(fname[0])

        # Add the polygon to the map
        layer = app.map.layer[group].layer["area_of_interest"]
        layer.set_data(gdf)

        # Create boundinx box based on area of interest
        aio_created(gdf.to_crs(app.crs), 0, 0)

        # change map position to center of polygon
        fly_to_site(gdf=gdf)

        # When a watershed was loaded, also use this as initial mask
        load_watershed = app.gui.getvar(group , "setup_grid_method") == "Load Watershed"
        if load_watershed:
            # Save filename as variable
            app.gui.setvar(group, "mask_init_fname", fname[0])
            # Add to GUI
            watershed_as_mask(gdf, group)

def open_watershed_selector(*args):
    """Method to open the selector of wathersheds"""
    group = "modelmaker_sfincs_hmt"
    # Open pop-up window
    okay, data = app.gui.popup(os.path.join(app.main_path, "misc", "select_watershed", "watershed.yml"), id="watershed", data=None)
    if not okay or not data:
        return
    # Add the polygon(s) to the map
    layer = app.map.layer[group].layer["area_of_interest"]
    gdf = gpd.GeoDataFrame.from_features(data, crs=4326)
    if len(gdf)>1: # If more that one watershed is provided try to combine
        gdf['new_column'] = 0
        gdf = gdf.dissolve(by='new_column')
    layer.set_data(gdf)

    # Create bounding box based on area of interest
    aio_created(gdf.to_crs(app.crs), 0, 0)

    # change map position to center of polygon
    fly_to_site(gdf=gdf)
    
    watershed_as_mask(gdf, group)
    
    
def watershed_as_mask(gdf, group):
    """"When a watershed was loaded, also use this as initial mask"""
    layer = app.map.layer[group].layer["mask_init"]
    layer.set_data(gdf)
    # Add to modelmaker
    app.toolbox[group].mask_init_polygon = gdf.to_crs(app.crs)
    # Change default settings of zmin zmax
    # TODO replace the numerical values for None 
    # (but that is now interpreted as a string in the GUI which causes trouble in hydromt_sfincs)
    app.gui.setvar(group, "mask_active_zmax", 10000.0)
    app.gui.setvar(group, "mask_active_zmin", -10000.0)

def grid_outline_created(gdf, index, id):
    """Function that specifies what happens when you create the bounding box"""

    group = "modelmaker_sfincs_hmt"

    if len(gdf) > 1:
        # Only keep the latest grid outline
        id0 = gdf["id"][0]
        app.map.layer[group].layer["grid_outline"].delete_feature(id0)
        gdf = gdf.drop([0]).reset_index(drop=True)

    # check if auto-select UTM is selected
    auto_select_utm = app.gui.getvar(group, "auto_select_utm")
    if auto_select_utm:
        gdf = update_crs(gdf=gdf)
        app.map.layer[group].layer["grid_outline"].gdf = update_rectangle_geometry(gdf=gdf)

    app.toolbox[group].grid_outline = gdf

    # check if bbox is defined
    if not gdf.empty:
        app.gui.setvar(group, "grid_outline", 1)

    # Remove area of interest (if present)
    if not app.map.layer[group].layer["area_of_interest"].gdf.empty:
        app.map.layer[group].layer["area_of_interest"].clear()
        app.toolbox[group].area_of_interest = gpd.GeoDataFrame()

    # Remove mask_init (if present)
    if not app.map.layer[group].layer["mask_init"].gdf.empty:
        app.map.layer[group].layer["mask_init"].clear()
        app.toolbox[group].mask_init_polygon = gpd.GeoDataFrame()

    # Remove current grid (if present)
    if app.map.layer["sfincs_hmt"].layer["grid"].data is not None:
        app.map.layer["sfincs_hmt"].layer["grid"].clear()

    update_geometry()
    app.gui.window.update()


def grid_outline_modified(gdf, index, id):
    """Function that specifies what happens when you modify the bounding box"""

    app.toolbox["modelmaker_sfincs_hmt"].grid_outline = gdf
    update_geometry()
    app.gui.window.update()


def aio_created(gdf, index, id):
    """Function that specifies what happens when you create the area of interest"""

    group = "modelmaker_sfincs_hmt"

    if len(gdf) > 1:
        # Remove the old area of interest
        id0 = gdf["id"][0]
        app.map.layer[group].layer["area_of_interest"].delete_feature(
            id0
        )
        gdf = gdf.drop([0]).reset_index(drop=True)

    # check if auto-select UTM is selected
    auto_select_utm = app.gui.getvar("modelmaker_sfincs_hmt", "auto_select_utm")
    if auto_select_utm:
        gdf = update_crs(gdf=gdf)

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

    # check if auto-rotate is selected and determine grid outline
    auto_rotate = app.gui.getvar(group, "auto_rotate")
    if auto_rotate:
        x0, y0, mmax, nmax, rot = utils.rotated_grid(
            gdf.unary_union, res, dec_origin=precision
        )
    else:
        x0, y0, x1, y1 = gdf.total_bounds
        x0, y0 = round(x0, precision), round(y0, precision)
        mmax = int(np.ceil((x1 - x0) / res))
        nmax = int(np.ceil((y1 - y0) / res))
        rot = 0

    # Remove current grid (if present)
    if app.map.layer["sfincs_hmt"].layer["grid"].data is not None:
        app.map.layer["sfincs_hmt"].layer["grid"].clear()

    # Remove mask_init (if present)
    if app.map.layer[group].layer["mask_init"].gdf.empty:
        app.map.layer[group].layer["mask_init"].clear()
        app.toolbox[group].mask_init_polygon = gpd.GeoDataFrame()

    # Set the new grid outline    
    app.gui.setvar(group, "x0", round(x0, precision))
    app.gui.setvar(group, "y0", round(y0, precision))
    app.gui.setvar(group, "mmax", mmax)
    app.gui.setvar(group, "nmax", nmax)
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )    
    app.gui.setvar(group, "rotation", round(rot, 3))

    # Redraw the grid outline
    redraw_rectangle()

    app.gui.window.update()

def aio_modified(gdf, index, id):
    """Function that specifies what happens when you modify the area of interest"""

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

    # check if auto-rotate is selected
    auto_rotate = app.gui.getvar(group, "auto_rotate")
    if auto_rotate:
        x0, y0, mmax, nmax, rot = utils.rotated_grid(
            gdf.unary_union, res, dec_origin=precision
        )
    else:
        x0, y0, x1, y1 = gdf.total_bounds
        x0, y0 = round(x0, precision), round(y0, precision)
        mmax = int(np.ceil((x1 - x0) / res))
        nmax = int(np.ceil((y1 - y0) / res))
        rot = 0
        
    # Set the new grid outline
    app.gui.setvar(group, "x0", round(x0, precision))
    app.gui.setvar(group, "y0", round(y0, precision))
    app.gui.setvar(group, "mmax", mmax)
    app.gui.setvar(group, "nmax", nmax)
    app.gui.setvar(
        group, "nr_cells", app.gui.getvar(group, "mmax") * app.gui.getvar(group, "nmax")
    )
    app.gui.setvar(group, "rotation", round(rot, 3))

    # Redraw the grid outline
    redraw_rectangle()

    # Update the window
    app.gui.window.update()

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

def generate_grid(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_grid()

def read_setup_yaml(*args):
    fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
    if fname[0]:
        app.toolbox["modelmaker_sfincs_hmt"].read_setup_yaml(fname[0])

def write_setup_yaml(*args):
    app.toolbox["modelmaker_sfincs_hmt"].write_setup_yaml()

def build(*args):
    app.toolbox["modelmaker_sfincs_hmt"].build()

## Help functions, no callbacks
    
def fly_to_site(gdf):
    """Fly to the site of the geodataframe"""

    # get the center of the polygon
    lon = gdf.to_crs(4326).geometry.centroid.x[0]
    lat = gdf.to_crs(4326).geometry.centroid.y[0]

    # specify a logical zoom level based on the extent of the bbox to make it fit in the window
    x0,y0,x1,y1 = gdf.to_crs(4326).geometry.total_bounds

    # use the width of the screen as well
    map_width = app.config["width"]
    map_height = app.config["height"]
    aspect_ratio = map_width / map_height

    zoom_level_width = math.floor(math.log2(360 * aspect_ratio / (x1-x0)))
    zoom_level_height = math.floor(math.log2(180 / (y1-y0)))

    zoom_level = min(zoom_level_width, zoom_level_height)

    # Fly to the site'
    app.map.fly_to(lon, lat, zoom_level)

def update_crs(gdf):
    """
    Update the coordinate system of the GUI (models and toolboxes) to the UTM zone 
    closest to the center of the gdf.

    Parameters:
    ----------
    gdf: geodataframe with a polygon

    """
    pyproj_crs = gis_utils.parse_crs(
        "utm", gdf.to_crs(4326).total_bounds
    )
    if pyproj_crs != app.crs:
        # pop-up warning
        ok = app.gui.window.dialog_yes_no(
            "The coordinate system of the GUI will be changed to {}. Continue?".format(pyproj_crs)
        )
        if ok:
            # change the coordinate system of the GUI
            coordinate_system.update_crs(pyproj_crs)
        
    return gdf.to_crs(app.crs)

def redraw_rectangle():
    """Redraw the grid outline based on the current settings"""

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

    gdf = app.map.layer[group].layer["grid_outline"].get_gdf()
    app.toolbox[group].grid_outline = gdf

    if not app.toolbox[group].grid_outline.empty:
        app.gui.setvar(group, "grid_outline", 1)
    else:
        app.gui.setvar(group, "grid_outline", 0)

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

def update_rectangle_geometry(gdf):
    """ Update some geodataframe attributes (needed for guitares) to make it suitable for the rectangle layer. 
    This is needed when the CRS is changed. """

    x0, y0, x1, y1 = gdf["geometry"].total_bounds

    gdf["x0"] = x0
    gdf["y0"] = y0
    gdf["dx"] = x1-x0
    gdf["dy"] = y1-y0
    gdf["rotation"] = 0

    return gdf
