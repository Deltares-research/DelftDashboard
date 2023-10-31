from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the boundary polygons
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_wlev"].activate()
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_outflow"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_active"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].activate()


def draw_wlev_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_wlev"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_wlev"].draw()


def delete_wlev_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "boundary_wlev_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon.loc[
        index, "id"
    ]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_wlev"].delete_feature(feature_id)
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].wlev_include_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "wlev_include_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon) - 1,
        )
    update()


def load_wlev_polygon(*args):
    pass


def save_wlev_polygon(*args):
    pass


def select_wlev_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon.loc[
        index, "id"
    ]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_wlev"].activate_feature(
        feature_id
    )


def wlev_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "wlev_polygon_index", nrp - 1)
    update()


def wlev_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon = gdf


def wlev_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "wlev_include_polygon_index", index)
    update()


def tick_box_wlev(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "wlev_reset", args[0])


def draw_outflow_polygon(*args):
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_outflow"].crs = app.crs
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_outflow"].draw()


def delete_outflow_polygon(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon) == 0:
        return
    index = app.gui.getvar("modelmaker_sfincs_hmt", "boundary_outflow_index")
    # or: iac = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon.loc[
        index, "id"
    ]
    # Delete from map
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_outflow"].delete_feature(
        feature_id
    )
    # Delete from app
    app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon = app.toolbox[
        "modelmaker_sfincs_hmt"
    ].outflow_include_polygon.drop(index)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon) - 1:
        app.gui.setvar(
            "modelmaker_sfincs_hmt",
            "outflow_include_polygon_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon) - 1,
        )
    update()


def load_outflow_polygon(*args):
    pass


def save_outflow_polygon(*args):
    pass


def select_outflow_polygon(*args):
    index = args[0]
    feature_id = app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon.loc[
        index, "id"
    ]
    app.map.layer["modelmaker_sfincs_hmt"].layer["mask_outflow"].activate_feature(
        feature_id
    )


def outflow_polygon_created(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon = gdf
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon)
    app.gui.setvar("modelmaker_sfincs_hmt", "outflow_include_polygon_index", nrp - 1)
    update()


def outflow_polygon_modified(gdf, index, id):
    app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon = gdf


def outflow_polygon_selected(index):
    app.gui.setvar("modelmaker_sfincs_hmt", "outflow_include_polygon_index", index)
    update()


def tick_box_outflow(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "outflow_reset", args[0])


def update():
    # loop through wlev polygons
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].wlev_include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_wlev_include_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "wlev_include_polygon_names", incnames)

    # loop through outflow polygons
    nrp = len(app.toolbox["modelmaker_sfincs_hmt"].outflow_include_polygon)
    incnames = []
    for ip in range(nrp):
        incnames.append(str(ip + 1))
    app.gui.setvar("modelmaker_sfincs_hmt", "nr_outflow_include_polygons", nrp)
    app.gui.setvar("modelmaker_sfincs_hmt", "outflow_include_polygon_names", incnames)

    app.gui.window.update()


def update_mask_bounds(*args):
    group = "modelmaker_sfincs_hmt"
    if app.gui.getvar(group, "mask_boundary_type") == 2:
        btype = "waterlevel"
    elif app.gui.getvar(group, "mask_boundary_type") == 3:
        btype = "outflow"
    app.toolbox[group].update_mask_bounds(btype=btype)


def reset_mask_bounds(*args):
    group = "modelmaker_sfincs_hmt"
    if app.gui.getvar(group, "mask_boundary_type") == 2:
        btype = "waterlevel"
    elif app.gui.getvar(group, "mask_boundary_type") == 3:
        btype = "outflow"
    app.toolbox["modelmaker_sfincs_hmt"].reset_mask_bounds(btype=btype)
