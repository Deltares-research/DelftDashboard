import numpy as np
import math
import os

from delftdashboard.app import app
from delftdashboard.operations import map

from hydromt_sfincs import utils
import time

class SfincsHmtDomain():
    long_name = "modelmaker_sfincs_hmt"

    def select(self, *args):
        # De-activate existing layers
        map.update()
        # Show the grid outline layer
        app.map.layer["sfincs_hmt"].layer["grid"].activate()
        app.map.layer[self.long_name].layer["grid_outline"].activate()
        app.map.layer[self.long_name].layer["area_of_interest"].activate()

    def select_model_type(*args):
        """" change default model extent methods for different model types"""	
        group = "modelmaker_sfincs_hmt"

        model_type = app.gui.getvar(group, "model_type_index")

        #model_type = 0 #overland
        #model_type = 1 #surge
        #model_type = 2 #quadtree

        if model_type == 0:
            app.gui.setvar(group, "mask_active_zmax", 10.0)
            app.gui.setvar(group, "mask_active_zmin", -10.0)
            app.gui.setvar(group, "mask_active_drop_area", 10.0)
            app.gui.setvar(group, "mask_active_fill_area", 10.0)
        elif model_type == 1:
            app.gui.setvar(group, "mask_active_zmax", 5.0)
            app.gui.setvar(group, "mask_active_zmin", -500.0)
            app.gui.setvar(group, "mask_active_drop_area", 10.0)
            app.gui.setvar(group, "mask_active_fill_area", 100.0)

        include_precip =  app.gui.getvar(group, "include_rainfall")
        # include_rivers = app.gui.getvar(group, "include_rivers")
        # include_waves = app.gui.setvar(group, "include_waves", False)    

        watershed = False
        if include_precip: #or include_rivers:
            watershed = True

        if model_type == 0 and watershed:
            # we recommend to use watershed data to setup the model extent
            app.gui.setvar(group, "setup_grid_methods_index", 2)
        elif model_type == 0 and not watershed:
            app.gui.setvar(group, "setup_grid_methods_index", 1)
        elif model_type == 1:
            app.gui.setvar(group, "setup_grid_methods_index", 0)


    def select_method(self, *args):
        app.gui.setvar(self.long_name, "setup_grid_methods_index", args[0])


    def draw_bbox(self, *args):
        group = self.long_name

        app.map.layer[group].layer["grid_outline"].crs = app.crs
        app.map.layer[group].layer["grid_outline"].draw()

    def draw_aio(self, *args):
        group = self.long_name

        app.map.layer[group].layer["area_of_interest"].crs = app.crs
        app.map.layer[group].layer["area_of_interest"].draw()



    def load_aio(self, *args):
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
            layer = app.map.layer[self.long_name].layer["area_of_interest"]
            layer.set_data(gdf)

            self.aio_created(gdf.to_crs(app.crs), 0, 0)

            if not app.map.layer[self.long_name].layer["grid_outline"].gdf.empty:
                app.gui.setvar(self.long_name, "grid_outline", 1)


    def fly_to_site(self, *args):
        gdf = app.toolbox[self.long_name].grid_outline
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


    def grid_outline_created(self, gdf, index, id):
        group = self.long_name
        if len(gdf) > 1:
            # Only keep the latest grid outline
            id0 = gdf["id"][0]
            app.map.layer[group].layer["grid_outline"].delete_feature(id0)
            gdf = gdf.drop([0]).reset_index(drop=True)
        app.toolbox[self.long_name].grid_outline = gdf

        # check if bbox is defined
        if not gdf.empty:
            app.gui.setvar(group, "grid_outline", 1)

        # Remove area of interest (if present)
        if not app.map.layer[group].layer["area_of_interest"].gdf.empty:
            app.map.layer[group].layer["area_of_interest"].clear()
        
        self.update_geometry()
        app.gui.window.update()


    def grid_outline_modified(self, gdf, index, id):
        app.toolbox[self.long_name].grid_outline = gdf
        self.update_geometry()
        app.gui.window.update()


    def aio_created(self, gdf, index, id):
        group = self.long_name
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
        self.redraw_rectangle()

        app.gui.window.update()


    def aio_modified(self, gdf, index, id):
        group = self.long_name
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
        self.redraw_rectangle()
        app.gui.window.update()


    def generate_grid(self, *args):
        app.toolbox[self.long_name].generate_grid()


    def update_geometry(self):
        group = self.long_name
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

    def edit_origin(self, *args):
        self.redraw_rectangle()


    def edit_nmmax(self, *args):
        self.redraw_rectangle()


    def edit_rotation(self, *args):
        self.redraw_rectangle()


    def edit_dxdy(self, *args):
        group = self.long_name
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

    def edit_res(self, *args):
        group = self.long_name
        
        # set dx and dy to res
        app.gui.setvar(group, "dx", app.gui.getvar(group, "res"))
        app.gui.setvar(group, "dy", app.gui.getvar(group, "res"))

        self.edit_dxdy(self, *args)

    def edit_domain(self, *args):
        toolbox_name = self.long_name
        path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
        pop_win_config_path  = os.path.join(path, "edit_domain.yml")
        okay, data = app.gui.popup(pop_win_config_path , None)
        if not okay:
            return

    def redraw_rectangle(self):
        group = self.long_name
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


    def read_setup_yaml(self, *args):
        fname = app.gui.window.dialog_open_file("Select yml file", filter="*.yml")
        if fname[0]:
            app.toolbox[self.long_name].read_setup_yaml(fname[0])


    def write_setup_yaml(self, *args):
        app.toolbox[self.long_name].write_setup_yaml()


    def build(self, *args):
        app.toolbox[self.long_name].build()
