from delftdashboard.app import app
from delftdashboard.operations import map

class SfincsHmtBoundaryMask():
    long_name = "modelmaker_sfincs_hmt"

    def select(self, *args):
        # De-activate existing layers
        map.update()
        # Show the boundary polygons
        app.map.layer[self.long_name].layer["mask_wlev"].activate()
        app.map.layer[self.long_name].layer["mask_outflow"].activate()
        # Show the grid and mask
        app.map.layer["sfincs_hmt"].layer["grid"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_active"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].activate()


    def draw_wlev_polygon(self, *args):
        app.map.layer[self.long_name].layer["mask_wlev"].crs = app.crs
        app.map.layer[self.long_name].layer["mask_wlev"].draw()


    def delete_wlev_polygon(self, *args):
        if len(app.toolbox[self.long_name].wlev_include_polygon) == 0:
            return
        index = app.gui.getvar(self.long_name, "boundary_wlev_index")
        # or: iac = args[0]
        feature_id = app.toolbox[self.long_name].wlev_include_polygon.loc[
            index, "id"
        ]
        # Delete from map
        app.map.layer[self.long_name].layer["mask_wlev"].delete_feature(feature_id)
        # Delete from app
        app.toolbox[self.long_name].wlev_include_polygon = app.toolbox[
            self.long_name
        ].wlev_include_polygon.drop(index)
        # If the last polygon was deleted, set index to last available polygon
        if index > len(app.toolbox[self.long_name].wlev_include_polygon) - 1:
            app.gui.setvar(
                self.long_name,
                "wlev_include_polygon_index",
                len(app.toolbox[self.long_name].wlev_include_polygon) - 1,
            )
        self.update()


    def load_wlev_polygon(self, *args):
        pass


    def save_wlev_polygon(self, *args):
        pass


    def select_wlev_polygon(self, *args):
        index = args[0]
        feature_id = app.toolbox[self.long_name].wlev_include_polygon.loc[
            index, "id"
        ]
        app.map.layer[self.long_name].layer["mask_wlev"].activate_feature(
            feature_id
        )


    def wlev_polygon_created(self, gdf, index, id):
        app.toolbox[self.long_name].wlev_include_polygon = gdf
        nrp = len(app.toolbox[self.long_name].wlev_include_polygon)
        app.gui.setvar(self.long_name, "wlev_polygon_index", nrp - 1)
        self.update()


    def wlev_polygon_modified(self, gdf, index, id):
        app.toolbox[self.long_name].wlev_include_polygon = gdf


    def wlev_polygon_selected(self, index):
        app.gui.setvar(self.long_name, "wlev_include_polygon_index", index)
        self.update()


    def tick_box_wlev(self, *args):
        app.gui.setvar(self.long_name, "wlev_reset", args[0])


    def draw_outflow_polygon(self, *args):
        app.map.layer[self.long_name].layer["mask_outflow"].crs = app.crs
        app.map.layer[self.long_name].layer["mask_outflow"].draw()


    def delete_outflow_polygon(self, *args):
        if len(app.toolbox[self.long_name].outflow_include_polygon) == 0:
            return
        index = app.gui.getvar(self.long_name, "boundary_outflow_index")
        # or: iac = args[0]
        feature_id = app.toolbox[self.long_name].outflow_include_polygon.loc[
            index, "id"
        ]
        # Delete from map
        app.map.layer[self.long_name].layer["mask_outflow"].delete_feature(
            feature_id
        )
        # Delete from app
        app.toolbox[self.long_name].outflow_include_polygon = app.toolbox[
            self.long_name
        ].outflow_include_polygon.drop(index)
        # If the last polygon was deleted, set index to last available polygon
        if index > len(app.toolbox[self.long_name].outflow_include_polygon) - 1:
            app.gui.setvar(
                self.long_name,
                "outflow_include_polygon_index",
                len(app.toolbox[self.long_name].outflow_include_polygon) - 1,
            )
        self.update()


    def load_outflow_polygon(self, *args):
        pass


    def save_outflow_polygon(self, *args):
        pass


    def select_outflow_polygon(self, *args):
        index = args[0]
        feature_id = app.toolbox[self.long_name].outflow_include_polygon.loc[
            index, "id"
        ]
        app.map.layer[self.long_name].layer["mask_outflow"].activate_feature(
            feature_id
        )


    def outflow_polygon_created(self, gdf, index, id):
        app.toolbox[self.long_name].outflow_include_polygon = gdf
        nrp = len(app.toolbox[self.long_name].outflow_include_polygon)
        app.gui.setvar(self.long_name, "outflow_include_polygon_index", nrp - 1)
        self.update()


    def outflow_polygon_modified(self, gdf, index, id):
        app.toolbox[self.long_name].outflow_include_polygon = gdf


    def outflow_polygon_selected(self, index):
        app.gui.setvar(self.long_name, "outflow_include_polygon_index", index)
        self.update()


    def tick_box_outflow(self, *args):
        app.gui.setvar(self.long_name, "outflow_reset", args[0])


    def update(self):
        # loop through wlev polygons
        nrp = len(app.toolbox[self.long_name].wlev_include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar(self.long_name, "nr_wlev_include_polygons", nrp)
        app.gui.setvar(self.long_name, "wlev_include_polygon_names", incnames)

        # loop through outflow polygons
        nrp = len(app.toolbox[self.long_name].outflow_include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar(self.long_name, "nr_outflow_include_polygons", nrp)
        app.gui.setvar(self.long_name, "outflow_include_polygon_names", incnames)

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
