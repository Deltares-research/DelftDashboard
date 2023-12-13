from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils
import geopandas as gpd
import os

class SfincsHmtCellMask():
    long_name = "modelmaker_sfincs_hmt"

    def select(self, *args):
        # De-activate existing layers
        map.update()
        # Show the mask include and exclude polygons
        app.map.layer[self.long_name].layer["mask_init"].activate()
        app.map.layer[self.long_name].layer["mask_include"].activate()
        app.map.layer[self.long_name].layer["mask_exclude"].activate()
        # Show the grid and mask
        app.map.layer["sfincs_hmt"].layer["grid"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_active"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].activate()
        app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].activate()

    def select_model_type(self, *args):
        group = self.long_name
        model_type = app.gui.getvar(group, "model_type")

        if model_type == 0: #inundation
            app.gui.setvar(group, "mask_active_zmax", 10.0)
            app.gui.setvar(group, "mask_active_zmin", -10.0)
            app.gui.setvar(group, "mask_active_drop_area", 10.0)
            app.gui.setvar(group, "mask_active_fill_area", 10.0)
        elif model_type == 1: #surge
            app.gui.setvar(group, "mask_active_zmax", 5.0)
            app.gui.setvar(group, "mask_active_zmin", -500.0)
            app.gui.setvar(group, "mask_active_drop_area", 10.0)
            app.gui.setvar(group, "mask_active_fill_area", 100.0)


    def select_mask_init_polygon_method(self, *args):
        app.gui.setvar(self.long_name, "mask_init_polygon_methods_index", args[0])


    def draw_mask_init_polygon(self, *args):
        app.map.layer[self.long_name].layer["mask_init"].crs = app.crs
        app.map.layer[self.long_name].layer["mask_init"].draw()


    def delete_mask_init_polygon(self, *args):
        if len(app.toolbox[self.long_name].mask_init_polygon) == 0:
            return

        gdf = app.toolbox[self.long_name].mask_init_polygon
        # gdf = gdf.drop(gdf.index, inplace=True)
        gdf = gpd.GeoDataFrame()

        app.toolbox[self.long_name].mask_init_polygon = gdf
        layer = app.map.layer[self.long_name].layer["mask_init"]
        layer.set_data(gdf)
        self.update()


    def load_mask_init_polygon(self, *args):
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

            # Add the polygon to the map
            layer = app.map.layer[self.long_name].layer["mask_init"]
            layer.set_data(gdf)

            self.mask_init_polygon_created(gdf, 0, 0)


    def save_mask_init_polygon(self, *args):
        pass


    def mask_init_polygon_created(self, gdf, index, id):
        app.toolbox[self.long_name].mask_init_polygon = gdf
        self.update()


    def mask_init_polygon_modified(self, gdf, index, id):
        app.toolbox[self.long_name].mask_init_polygon = gdf


    def draw_include_polygon(self, *args):
        app.map.layer[self.long_name].layer["mask_include"].crs = app.crs
        app.map.layer[self.long_name].layer["mask_include"].draw()


    def delete_include_polygon(self, *args):
        if len(app.toolbox[self.long_name].mask_include_polygon) == 0:
            return
        index = app.gui.getvar(self.long_name, "mask_include_polygon_index")
        # or: iac = args[0]
        feature_id = app.toolbox[self.long_name].mask_include_polygon.loc[
            index, "id"
        ]
        # Delete from map
        app.map.layer[self.long_name].layer["mask_include"].delete_feature(
            feature_id
        )
        # Delete from app
        app.toolbox[self.long_name].mask_include_polygon = app.toolbox[
            self.long_name
        ].mask_include_polygon.drop(index)
        # If the last polygon was deleted, set index to last available polygon
        if index > len(app.toolbox[self.long_name].mask_include_polygon) - 1:
            app.gui.setvar(
                self.long_name,
                "mask_include_polygon_index",
                len(app.toolbox[self.long_name].mask_include_polygon) - 1,
            )
        self.update()


    def load_include_polygon(self, *args):
        pass


    def save_include_polygon(self, *args):
        pass


    def select_include_polygon(self, *args):
        index = args[0]
        feature_id = app.toolbox[self.long_name].mask_include_polygon.loc[
            index, "id"
        ]
        app.map.layer[self.long_name].layer["mask_include"].activate_feature(
            feature_id
        )


    def include_polygon_created(self, gdf, index, id):
        app.toolbox[self.long_name].mask_include_polygon = gdf
        nrp = len(app.toolbox[self.long_name].mask_include_polygon)
        app.gui.setvar(self.long_name, "mask_include_polygon_index", nrp - 1)
        self.update()


    def include_polygon_modified(self, gdf, index, id):
        app.toolbox[self.long_name].mask_include_polygon = gdf


    def include_polygon_selected(self, index):
        app.gui.setvar(self.long_name, "mask_include_polygon_index", index)
        self.update()


    def draw_exclude_polygon(self, *args):
        app.map.layer[self.long_name].layer["mask_exclude"].draw()


    def delete_exclude_polygon(self, *args):
        if len(app.toolbox[self.long_name].mask_exclude_polygon) == 0:
            return
        index = app.gui.getvar(self.long_name, "mask_exclude_polygon_index")
        # or: iac = args[0]
        feature_id = app.toolbox[self.long_name].mask_exclude_polygon.loc[
            index, "id"
        ]
        # Delete from map
        app.map.layer[self.long_name].layer["mask_exclude"].delete_feature(
            feature_id
        )
        # Delete from app
        app.toolbox[self.long_name].mask_exclude_polygon = app.toolbox[
            self.long_name
        ].mask_exclude_polygon.drop(index)
        # If the last polygon was deleted, set index to last available polygon
        if index > len(app.toolbox[self.long_name].mask_exclude_polygon) - 1:
            app.gui.setvar(
                self.long_name,
                "mask_exclude_polygon_index",
                len(app.toolbox[self.long_name].mask_exclude_polygon) - 1,
            )
        self.update()


    def load_exclude_polygon(self, *args):
        pass


    def save_exclude_polygon(self, *args):
        pass


    def select_exclude_polygon(self, *args):
        index = args[0]
        feature_id = app.toolbox[self.long_name].mask_exclude_polygon.loc[
            index, "id"
        ]
        app.map.layer[self.long_name].layer["mask_exclude"].activate_feature(
            feature_id
        )


    def exclude_polygon_created(self, gdf, index, id):
        app.toolbox[self.long_name].mask_exclude_polygon = gdf
        nrp = len(app.toolbox[self.long_name].mask_exclude_polygon)
        app.gui.setvar(self.long_name, "mask_exclude_polygon_index", nrp - 1)
        self.update()


    def exclude_polygon_modified(self, gdf, index, id):
        app.toolbox[self.long_name].mask_exclude_polygon = gdf


    def exclude_polygon_selected(self, index):
        app.gui.setvar(self.long_name, "mask_exclude_polygon_index", index)
        self.update()


    def mask_add_tick_box(self, *args):
        app.gui.setvar(self.long_name, "mask_active_add", args[0])

    def mask_del_tick_box(self, *args):
        app.gui.setvar(self.long_name, "mask_active_del", args[0])

    def tick_box(self, *args):
        app.gui.setvar(self.long_name, "mask_active_reset", args[0])

    def edit_mask_active(self, *args):
        toolbox_name = self.long_name
        path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
        pop_win_config_path  = os.path.join(path, "edit_mask_active.yml")
        okay, data = app.gui.popup(pop_win_config_path , None)
        if not okay:
            return

    def update(self):
        nrp = len(app.toolbox[self.long_name].mask_init_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar(self.long_name, "nr_mask_polygons", nrp)

        nrp = len(app.toolbox[self.long_name].mask_include_polygon)
        incnames = []
        for ip in range(nrp):
            incnames.append(str(ip + 1))
        app.gui.setvar(self.long_name, "nr_mask_include_polygons", nrp)
        app.gui.setvar(self.long_name, "mask_include_polygon_names", incnames)

        nrp = len(app.toolbox[self.long_name].mask_exclude_polygon)
        excnames = []
        for ip in range(nrp):
            excnames.append(str(ip + 1))
        app.gui.setvar(self.long_name, "nr_mask_exclude_polygons", nrp)
        app.gui.setvar(self.long_name, "mask_exclude_polygon_names", excnames)

        app.gui.window.update()


    def update_mask_active(self, *args):
        app.toolbox[self.long_name].update_mask_active()
