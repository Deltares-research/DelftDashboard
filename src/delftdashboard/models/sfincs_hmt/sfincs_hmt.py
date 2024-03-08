import os
import numpy as np
import xarray as xr

from hydromt_sfincs import SfincsModel

from delftdashboard.app import app
from delftdashboard.operations.model import GenericModel

from .observation_points import add_observation_point
from .observation_points import select_observation_point_from_map
from .boundary_conditions_wlev import add_boundary_point
from .boundary_conditions_wlev import select_boundary_point_from_map
from .boundary_conditions_dis import select_discharge_point_from_map

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "SFINCS (HydroMT)"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()
        self.set_gui_variables()

    def initialize_domain(self):
        root = os.getcwd()
        self.domain = SfincsModel(
            data_libs=app.config["data_libs"],
            root=root,
            mode="w+",
        )
        self.set_crs()

    def set_crs(self):
        crs = app.crs
        if self.domain.crs != crs:
            self.domain.set_crs(crs)

            # change default resolutions
            group = "modelmaker_sfincs_hmt"
            if app.crs.is_geographic:
                app.gui.setvar(group, "dx", 0.1)
                app.gui.setvar(group, "dy", 0.1)
                app.gui.setvar(group, "res", 0.1)
                app.gui.setvar(group, "unit", " (in \u00B0)")
            else:
                app.gui.setvar(group, "dx", 500)
                app.gui.setvar(group, "dy", 500)
                app.gui.setvar(group, "res", 500)
                app.gui.setvar(group, "unit", " (in m)")

        # update map
        self.plot()

    def select_working_directory(self):
        root = os.getcwd()
        if self.domain.root != root:
            self.domain.set_root(root=root, mode="w+")

    def add_layers(self):
        # Add main app layer
        layer = app.map.add_layer("sfincs_hmt")

        layer.add_layer(
            "grid",
            type="line",
            circle_radius=0,
            line_width=0.5,
            line_color="black",
            line_width_inactive=0.5,
            line_color_inactive="lightgrey", #TODO fix this
            line_opacity_inactive=0.5,
        )

        # TODO make this a PolygonLayer (but not yet proeprly implemented in Guitares)
        layer.add_layer(
            "region",
            type="draw",
            shape="polygon",
            polygon_line_color="grey",
            polygon_fill_opacity=0.3,
        )

        bed_levels = layer.add_layer(
            "bed_levels",
            type="raster",
        )

        # Set update method for topography layer
        bed_levels.update = update_map

        layer.add_layer(
            "mask",
            type="circle",
            circle_radius=3,
            legend_position="top-right",
            legend_title="Cell type",
            fill_color="yellow",
            line_color="transparent",
            big_data=True,
        )

        layer.add_layer(
            "boundary_points",
            type="circle_selector",
            select=select_boundary_point_from_map,
            line_color="black",
            line_opacity=1.0,
            fill_color="darkblue",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="darkblue",
            hover_property="name",
        )

        layer.add_layer(
            "discharge_points",
            type="circle_selector",
            select=select_discharge_point_from_map,
            line_color="black",
            line_opacity=1.0,
            fill_color="darkgreen",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="darkgreen",
            hover_property="name",
        )

        layer.add_layer(
            "observation_points",
            type="circle_selector",
            select=select_observation_point_from_map,
            line_color="black",
            line_opacity=1.0,
            fill_color="black",
            fill_opacity=1.0,
            circle_radius=4,
            circle_radius_selected=5,
            line_color_selected="white",
            fill_color_selected="black",
            hover_property="name",
        )

        layer.add_layer(
            "cross_sections",
            type="line_selector",
            line_color="white",
            line_opacity=1.0,
            fill_color="blue",
            fill_opacity=1.0,
            circle_radius=3,
            circle_radius_selected=4,
            line_color_selected="white",
            fill_color_selected="red",
        )

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Grid is made inactive
            app.map.layer["sfincs_hmt"].layer["grid"].deactivate()
            app.map.layer["sfincs_hmt"].layer["region"].hide()

            # Bed levels are hidden
            app.map.layer["sfincs_hmt"].layer["bed_levels"].hide()

            # Mask is made invisible
            app.map.layer["sfincs_hmt"].layer["mask"].hide()

            # Hide structure layers
            if 'measures' in app.map.layer["sfincs_hmt"].layer:
                app.map.layer["sfincs_hmt"].layer["measures"].hide()

            # Boundary points are made grey
            app.map.layer["sfincs_hmt"].layer["boundary_points"].deactivate()
            app.map.layer["sfincs_hmt"].layer["discharge_points"].deactivate()


            # Observation points are made grey
            app.map.layer["sfincs_hmt"].layer["observation_points"].deactivate()
            app.map.layer["sfincs_hmt"].layer["cross_sections"].deactivate()
        if mode == "invisible":
            app.map.layer["sfincs_hmt"].hide()

    def set_gui_variables(self):
        # Copies sfincs input to gui variables
        group = "sfincs_hmt"

        for var_name in self.domain.config:
            try:
                app.gui.setvar(group, var_name, self.domain.config.get(var_name))
            except:
                print("No GUI variable " + var_name)

        app.gui.setvar(group, "roughness_type", "landsea")

        # Now set some extra variables needed for SFINCS GUI
        app.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        app.gui.setvar(group, "input_options_values", ["bin", "asc"])

        app.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        app.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])

        app.gui.setvar(group, "meteo_forcing_type", "uniform")

        # Boundary conditions
        # Waterlevel boundary methods
        bc_wlev_methods = ["Click Points", "Generate along Boundary", "Select from Database", "Load from File"]
        bc_wlev_timeseries_methods = ["Constant timeseries", "Guassian timeseries", "Download from database"]
        app.gui.setvar(group, "bc_wlev_methods", bc_wlev_methods)
        app.gui.setvar(group, "bc_wlev_methods_index", 0)
        app.gui.setvar(group, "bc_wlev_timeseries_methods", bc_wlev_timeseries_methods)
        app.gui.setvar(group, "bc_wlev_timeseries_methods_index", 0)

        # values
        app.gui.setvar(group, "bc_wlev_value", 0.0)
        app.gui.setvar(group, "bc_dist_along_msk", 5e3)
        app.gui.setvar(group, "merge_bc_wlev", True)

        # gui settings
        app.gui.setvar(group, "boundary_point_names", [])
        app.gui.setvar(group, "nr_boundary_points", 0)
        app.gui.setvar(group, "active_boundary_point", 0)

        # Discharge methods
        bc_dis_methods = ["Click Points", "Load from File"]
        bc_dis_timeseries_methods = ["Constant timeseries", "Guassian timeseries"]
        app.gui.setvar(group, "bc_dis_methods", bc_dis_methods)
        app.gui.setvar(group, "bc_dis_methods_index", 0)
        app.gui.setvar(group, "bc_dis_timeseries_methods", bc_dis_timeseries_methods)
        app.gui.setvar(group, "bc_dis_timeseries_methods_index", 0)

        # values
        app.gui.setvar(group, "bc_dis_value", 0.0)
        app.gui.setvar(group, "merge_bc_dis", True)

        # gui settings
        app.gui.setvar(group, "discharge_point_names", [])
        app.gui.setvar(group, "nr_discharge_points", 0)
        app.gui.setvar(group, "active_discharge_point", 0)

        # Observation points 
        obs_methods = ["Click Points", "Select from Database", "Load from File"]
        app.gui.setvar(group, "obs_methods", obs_methods)
        app.gui.setvar(group, "obs_methods_index", 0)
        app.gui.setvar(group, "observation_point_names", [])
        app.gui.setvar(group, "nr_observation_points", 0)
        app.gui.setvar(group, "active_observation_point", 0)

        crs_methods = ["Draw LineString", "Load from File"]
        app.gui.setvar(group, "crs_methods", crs_methods)
        app.gui.setvar(group, "crs_methods_index", 0)
        app.gui.setvar(group, "cross_section_names", [])
        app.gui.setvar(group, "nr_cross_sections", 0)
        app.gui.setvar(group, "active_cross_section", 0)

        app.gui.setvar(group, "depthcontour_value", 0.0)
        app.gui.setvar(group, "flowboundarypoints_length", 0)
        app.gui.setvar(group, "boundaryspline_length", 0)
        app.gui.setvar(group, "boundaryspline_filename", "")
        app.gui.setvar(group, "boundaryspline_flowdx", 0.0)
        app.gui.setvar(group, "boundaryconditions_zs", 0.0)
        app.gui.setvar(group, "wind", True)
        app.gui.setvar(group, "rain", True)

        # Structures
        app.gui.setvar(group, "structure_weirs_methods", ["Draw LineString", "Load from file"])
        app.gui.setvar(group, "structure_weirs_method_index", 0)
        app.gui.setvar(group, "structure_weir_index", None)
        app.gui.setvar(group, "structure_weir_list", [])
        app.gui.setvar(group, "active_structure_weir", 0)

        app.gui.setvar(group, "structure_thin_dam_methods", ["Draw LineString", "Load from file"])
        app.gui.setvar(group, "structure_thin_dam_method_index", 0)
        app.gui.setvar(group, "structure_thd_index", None)
        app.gui.setvar(group, "structure_thd_list", [])
        app.gui.setvar(group, "active_structure_thd", 0)

        app.gui.setvar(group, "structure_drainage_methods", ["Draw LineString", "Load from file"])
        app.gui.setvar(group, "structure_drainage_method_index", 0)
        app.gui.setvar(group, "structure_drn_index", None)
        app.gui.setvar(group, "structure_drn_list", [])
        app.gui.setvar(group, "active_structure_drn", 0)
        app.gui.setvar(group, "drainage_type", 0)

        # Physics
        app.gui.setvar(group, "advection", 0)
        app.gui.setvar(group, "coriolis", 0)

        # Output
        app.gui.setvar(group, "storetwet", 0)
        app.gui.setvar(group, "storevelmax", 0)
        app.gui.setvar(group, "storecumprcp", 0)
        app.gui.setvar(group, "storemaxwind", 0)

    def set_model_variables(self, varid=None, value=None):
        # Copies gui variables to sfincs input
        group = "sfincs_hmt"

        for var_name in self.domain.config:
            if var_name == "epsg":
                self.domain.set_config(var_name, app.crs.to_epsg())
            else:
                try:
                    self.domain.set_config(
                        var_name, app.gui.variables[group][var_name]["value"]
                    )
                except:
                    print("No GUI variable " + var_name + " in sfincs input file")

    def open(self):
        # Open input file, and change working directory
        fname = app.gui.window.dialog_open_file(
            "Open SFINCS input file", filter="*.inp"
        )
        if fname:
            root = os.path.dirname(fname)
            self.domain.set_root(root=root, mode="r")
            self.domain.read()

            # Change working directory
            os.chdir(root)

            # Change CRS
            app.crs = self.domain.crs

    def save(self):
        # Save sfincs input
        mode = (
            "r+"
            if self.domain._write and self.domain._read
            else ("w" if self.domain._write else "r")
        )

        if mode == "r":
            q = app.gui.window.dialog_yes_no(
                "Do you want to overwrite the existing model?"
            )
            if q.Yes:
                self.domain.set_root(root=fname, mode="w+")
            else:
                fname = app.gui.window.dialog_select_path(
                    "Select the directory where you want to store your model",
                    path=os.getcwd(),
                )
                self.domain.set_root(root=fname, mode="w+")

        # Write sfincs model
        self.domain.write()
        # write setup yml file
        app.toolbox["modelmaker_sfincs_hmt"].write_setup_yaml()

        # self.domain.write_batch_file()

    def load(self):
        self.domain.read()
        self.plot()

    def plot(self):
        pass

    def add_stations(self, gdf, naming_option="name", model_option="obs"):
        # if id is used as naming option, rename column
        if naming_option == "id":
            gdf = gdf.rename(columns={"id": "name"})

        if model_option == "obs":
            add_observation_point(gdf)
        elif model_option == "bnd":
            add_boundary_point(gdf)


def update_map():
    # check if map extent is available
    if not app.map.map_extent:
        print("Map extent not yet available ...")
        return
    
    # check if bed_levels layer is visible
    if not app.map.layer["sfincs_hmt"].layer["bed_levels"].visible:
        return

    # check if grid is already defined
    grid = app.model["sfincs_hmt"].domain.grid
    if "dep" in grid:
        da_dep = grid["dep"]
        if np.isnan(da_dep).all():
            return
    else:
        return

    if "msk" in grid:
        da_dep = da_dep.where(grid["msk"] > 0)

    coords = app.map.map_extent
    xl = [coords[0][0], coords[1][0]]
    yl = [coords[0][1], coords[1][1]]
    wdt = app.map.view.geometry().width()

    npix = wdt

    dxy = (xl[1] - xl[0]) / npix
    xv = np.arange(xl[0], xl[1], dxy)
    yv = np.arange(yl[0], yl[1], dxy)

    # initilize empty xarray
    da_like = xr.DataArray(
        np.float32(np.full([len(yv), len(xv)], np.nan)),
        coords={"y": yv, "x": xv},
        dims=["y", "x"],
    )
    da_like.raster.set_crs(4326)

    da_dep = da_dep.raster.reproject_like(da_like, method="bilinear").load()

    da_dep.raster.set_nodata(np.nan)

    app.map.layer["sfincs_hmt"].layer["bed_levels"].set_data(
        x=xv,
        y=yv,
        z=da_dep.values,
        colormap=app.color_map_earth,
        decimals=1,
        legend_title="Bed levels [m+ref]",
    )
