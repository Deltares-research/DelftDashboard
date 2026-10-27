"""Flood map toolbox for DelftDashboard.

Provides the main Toolbox class for generating and visualizing flood maps
from model output, including topobathy and index GeoTIFF management.
"""

import os

import geopandas as gpd
import xarray as xr
from cht_tiling import FloodMap

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

from .utils import make_topobathy_cog


class Toolbox(GenericToolbox):
    """Toolbox for flood map generation and visualization."""

    def __init__(self, name: str) -> None:
        """Initialize the flood map toolbox.

        Parameters
        ----------
        name : str
            Name identifier for the toolbox.
        """
        super().__init__()

        self.name = name
        self.long_name = "Flood Map"

    def initialize(self) -> None:
        """Set up default GUI variables and flood map state."""
        group = "flood_map"

        app.gui.setvar(group, "dx_geotiff", 10.0)
        app.gui.setvar(group, "map_file_name", "")
        app.gui.setvar(group, "topo_file_string", "File : ")
        app.gui.setvar(group, "index_file_string", "File : ")
        app.gui.setvar(group, "map_file_string", "File : ")
        app.gui.setvar(group, "instantaneous_or_maximum", "maximum")
        app.gui.setvar(group, "available_time_strings", [""])
        app.gui.setvar(group, "time_index", 0)
        app.gui.setvar(group, "flood_map_opacity", 0.7)
        app.gui.setvar(group, "continuous_or_discrete_colors", "discrete")
        app.gui.setvar(group, "cmap", "jet")
        app.gui.setvar(group, "cmin", 0.0)
        app.gui.setvar(group, "cmax", 2.0)
        app.gui.setvar(group, "colormaps", app.gui.getvar("view_settings", "colormaps"))

        self.flood_map = FloodMap()
        # Set some default values
        self.flood_map.cmap = app.gui.getvar(group, "cmap")
        self.flood_map.cmin = app.gui.getvar(group, "cmin")
        self.flood_map.cmax = app.gui.getvar(group, "cmax")
        self.flood_map.color_values = "default"  # Using green, yellow, orange, red
        self.flood_map.discrete_colors = True

        # Exclude polygons SnapWave
        self.polygon = gpd.GeoDataFrame()

        self.instantaneous_time_strings = [""]
        self.maximum_time_strings = [""]
        self.nr_of_instantaneous_times = 0
        self.nr_of_maximum_times = 0

    def set_layer_mode(self, mode: str) -> None:
        """Control visibility of flood map layers.

        Parameters
        ----------
        mode : str
            One of ``"active"``, ``"inactive"``, or ``"invisible"``.
        """
        if mode == "active":
            # Make container layer visible
            app.map.layer["flood_map"].show()
            # Always show track layer
            app.map.layer["flood_map"].layer["flood_map"].show()
            app.map.layer["flood_map"].layer["polygon"].hide()

        elif mode == "inactive":
            # Make all layers invisible
            app.map.layer[self.name].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer[self.name].hide()

    def add_layers(self) -> None:
        """Register map layers for the flood map toolbox."""
        layer = app.map.add_layer(self.name)
        layer.add_layer(
            "flood_map",
            type="raster_image",
            opacity=0.7,
            legend_position="bottom-right",
        )
        # Open boundary
        from .topobathy import polygon_created

        layer.add_layer(
            "polygon",
            type="draw",
            shape="polygon",
            create=polygon_created,
            polygon_line_color="deepskyblue",
            polygon_fill_color="deepskyblue",
            polygon_fill_opacity=0.1,
        )

    def load_topobathy_geotiff(self) -> None:
        """Select and load a topo/bathy GeoTIFF file via dialog."""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
            "Select topo/bathy geotiff file", filter="*.tif"
        )
        if not full_name:
            return
        self.topobathy_geotiff = full_name
        self.flood_map.set_topobathy_file(full_name)

    def generate_topobathy_geotiff(self) -> None:
        """Generate a topobathy COG from the selected datasets."""
        if self.polygon.empty:
            model = app.active_model
            if model.name == "sfincs_cht":
                bounds = model.domain.grid.bounds()
            elif model.name == "sfincs_hmt":
                exterior = model.domain.quadtree_grid.exterior
                if len(exterior) == 0:
                    app.gui.window.dialog_warning("No grid found!")
                    return
                bounds = exterior.total_bounds
            elif model.name == "hurrywave_hmt":
                exterior = model.domain.quadtree_grid.exterior
                if len(exterior) == 0:
                    app.gui.window.dialog_warning("No grid found!")
                    return
                bounds = exterior.total_bounds
            else:
                app.gui.window.dialog_warning(
                    f"Model '{model.name}' not supported for topobathy generation."
                )
                return
        else:
            bounds = self.polygon.total_bounds

        dx = app.gui.getvar("flood_map", "dx_geotiff")
        full_name, path, name, ext, fltr = app.gui.window.dialog_save_file(
            "Save topo/bathy geotiff file", filter="*.tif"
        )
        if not full_name:
            return
        filename = full_name
        wb = app.gui.window.dialog_wait("Generating topobathy geotiff ...")
        try:
            make_topobathy_cog(
                filename,
                app.selected_bathymetry_datasets,
                bounds,
                app.map.crs,
                topography_data_catalog=app.topography_data_catalog,
                dx=dx,
            )
            self.topobathy_geotiff = filename
            self.flood_map.set_topobathy_file(filename)
        except Exception as e:
            import traceback

            traceback.print_exc()
            wb.close()
            app.gui.window.dialog_warning(f"Error generating topobathy:\n{e}")
            return
        wb.close()

    def load_index_geotiff(self) -> None:
        """Select and load an index GeoTIFF file via dialog."""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
            "Select index geotiff file", filter="*.tif"
        )
        if not full_name:
            return
        self.index_geotiff = full_name
        self.flood_map.set_index_file(full_name)

    def generate_index_geotiff(self) -> None:
        """Generate an index COG mapping grid cells to topobathy pixels."""
        model = app.active_model
        if model.name == "sfincs_cht":
            grid = model.domain.grid
        elif model.name == "sfincs_hmt":
            grid = model.domain.quadtree_grid
        else:
            app.gui.window.dialog_warning(
                f"Model '{model.name}' not supported for index generation."
            )
            return

        full_name, path, name, ext, fltr = app.gui.window.dialog_save_file(
            "Save index geotiff file", filter="*.tif"
        )
        if not full_name:
            return
        wb = app.gui.window.dialog_wait("Generating index geotiff ...")
        try:
            if model.name == "sfincs_hmt":
                grid.create_index_cog(
                    full_name, app.toolbox["flood_map"].topobathy_geotiff
                )
            else:
                grid.make_index_cog(
                    full_name, app.toolbox["flood_map"].topobathy_geotiff
                )
            self.flood_map.set_index_file(full_name)
            self.index_geotiff = full_name
        except Exception as e:
            import traceback

            traceback.print_exc()
            wb.close()
            app.gui.window.dialog_warning(f"Error generating index:\n{e}")
            return
        wb.close()

    def load_map_output(self) -> None:
        """Load model map output from a NetCDF file."""
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        # Use full path
        if file_name[0]:
            # Read the map output
            self.map_file_name = file_name[0]

            self.dsa = xr.open_dataset(self.map_file_name)

            # Instantaneous
            times = self.dsa.time.values
            dt_list = times.astype("datetime64[s]").astype(object)
            self.instantaneous_time_strings = [
                dt.strftime("%Y-%m-%d %H:%M:%S") for dt in dt_list
            ]
            self.nr_of_instantaneous_times = len(self.instantaneous_time_strings)

            # Maximum
            max_times = self.dsa.timemax.values
            dt_list = max_times.astype("datetime64[s]").astype(object)
            self.maximum_time_strings = [
                dt.strftime("%Y-%m-%d %H:%M:%S") for dt in dt_list
            ]
            self.nr_of_maximum_times = len(self.maximum_time_strings)

            app.gui.setvar("flood_map", "time_index", 0)

    def update_flood_map(self) -> None:
        """Update the flood map layer with the current time step data."""
        instantaneous_or_maximum = app.gui.getvar(
            "flood_map", "instantaneous_or_maximum"
        )

        if instantaneous_or_maximum == "instantaneous":
            if self.nr_of_instantaneous_times == 0:
                app.map.layer["flood_map"].layer["flood_map"].clear()
                return
        else:
            if self.nr_of_maximum_times == 0:
                app.map.layer["flood_map"].layer["flood_map"].clear()
                return

        itime = app.gui.getvar("flood_map", "time_index")

        if instantaneous_or_maximum == "instantaneous":
            zs = self.dsa.zs.isel(time=itime).values[:]
        else:
            zs = self.dsa.zsmax.isel(timemax=itime).values[:]

        self.flood_map.set_water_level(zs)

        app.map.layer[self.name].layer["flood_map"].set_data(self.flood_map)

    def load_his_output(self) -> None:
        """Load history output from a NetCDF file."""
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        if file_name[0]:
            self.tc.read_track(file_name[0])
            self.tc.name = os.path.basename(file_name[0]).split(".")[0]
            app.gui.setvar("tropical_cyclone", "ensemble_start_time", None)
            app.gui.setvar("tropical_cyclone", "ensemble_start_time_index", 0)
            app.gui.setvar("tropical_cyclone", "track_loaded", True)
            self.plot_track()

    def export_flood_map(self) -> None:
        """Export the flood map to a GeoTIFF file."""
        file_name = app.gui.window.dialog_save_file("Export flood map", "*.tif")
        if file_name[0]:
            wb = app.gui.window.dialog_wait("Exporting flood map ...")
            self.flood_map.make()
            self.flood_map.write(file_name[0])
            wb.close()
