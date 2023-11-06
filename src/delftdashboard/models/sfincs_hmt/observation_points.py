from delftdashboard.app import app
from delftdashboard.operations import map

import geopandas as gpd
from hydromt_sfincs import utils

def select(*args):
    map.update()
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_mode("active")
    update()

def edit(*args):
    app.model["sfincs_hmt"].set_model_variables()

def add_observation_point(gdf, merge=True):
    model = app.model["sfincs_hmt"].domain
    model.setup_observation_points(locations = gdf, merge=merge)

    index = len(model.geoms["obs"]) - 1
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_data(model.geoms["obs"], index)
    app.gui.setvar("sfincs_hmt", "active_observation_point", index)


def load(*args):
    # map.reset_cursor()

    rsp = app.gui.window.dialog_open_file("Select file with observation points ...",
                                          filter="*.obs *.shp *.geojson")

    if rsp[0]:
        model = app.model["sfincs_hmt"].domain

        if rsp[2].endswith(".obs"):
            # read observation points from existing model
            gdf = utils.read_xyn(fn=rsp[0], crs=model.crs)
            model.set_geoms(gdf, name="obs")
        else:
            gdf = model.data_catalog.get_geodataframe(
                rsp[0],
                bbox=model.mask.raster.transform_bounds(4326),
                assert_gtype="Point",
            )

        if len(gdf.index) == 0:
            app.gui.window.dialog_info("No valid observation points found within model domain!")
            return
        
        # make sure the observation points have a name
        if "name" not in gdf.columns:
            gdf["name"] = "Point " + gdf.index.astype(str)

        ok = app.gui.window.dialog_yes_no("Do you want to merge the observation points with the existing ones?")

        add_observation_point(gdf, merge=ok)
        update()

def save(*args):
    map.reset_cursor()

    model = app.model["sfincs_hmt"].domain
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name="sfincs.obs",
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        model.set_config("obsfile", rsp[2])
        model.write_geoms(data_vars="obs")

def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)

def point_clicked(x, y):
    # Point clicked on map. Add observation point.
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        # Cancel was clicked
        return    
    if name in app.gui.getvar("sfincs_hmt", "observation_point_names"):
        app.gui.window.dialog_info("An observation point with this name already exists!")
        return
    
    # create gdf from xy
    geometry = gpd.points_from_xy([x], [y])
    gdf = gpd.GeoDataFrame(geometry=geometry, crs=app.crs)
    gdf["name"] = name

    add_observation_point(gdf, merge=True)
    update()

def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar("sfincs_hmt", "active_observation_point")
    app.map.layer["sfincs_hmt"].layer["observation_points"].select_by_index(index)

def select_observation_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar("sfincs_hmt", "active_observation_point", index)
    app.gui.window.update()

def delete_point_from_list(*args):
    map.reset_cursor()

    model = app.model["sfincs_hmt"].domain
    index = app.gui.getvar("sfincs_hmt", "active_observation_point")

    # delete point from observation points
    model.geoms["obs"] = model.geoms["obs"].drop(index=index)

    if len(model.geoms["obs"].index) == 0:
        # no more observation points left
        model.geoms.pop("obs")
        app.map.layer["sfincs_hmt"].layer["observation_points"].clear()
        update()
    else:
        # set new index
        index = index - 1 if index > 0 else 0
        app.map.layer["sfincs_hmt"].layer["boundary_points"].set_data(model.geoms["obs"], index)
        app.gui.setvar("sfincs_hmt", "active_boundary_point", index)        
    update()

def update():
    # get observation points
    gdf = app.map.layer["sfincs_hmt"].layer["observation_points"].data
    if gdf is None:
        return
    
    names = []
    for index, row in gdf.iterrows():
        names.append(row["name"])

    app.gui.setvar("sfincs_hmt", "observation_point_names", names)
    app.gui.setvar("sfincs_hmt", "nr_observation_points", len(gdf.index))
    app.gui.window.update()