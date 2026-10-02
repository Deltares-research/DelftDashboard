"""Flood map toolbox for DelftDashboard.

Provides the main Toolbox class for generating and visualizing flood maps
from model output, including topobathy and index GeoTIFF management.
"""

import os

import geopandas as gpd
import xarray as xr
from hydromt_sfincs.workflows.flood_map import FloodMap

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
        app.gui.setvar(group, "subgrid_file_string", "File : ")
        app.gui.setvar(group, "flood_map_method", "level")
        app.gui.setvar(group, "max_jump", 1.0)
        app.gui.setvar(group, "max_residual_relief", 10.0)
        # Slope-method settings without a GUI control: blending of the
        # neighbouring cell surfaces and the flat-level (ponded water) rule
        # are always on; the rule's tuning parameters keep these defaults.
        self.flat_level_ratio = 0.2
        self.flat_level_min_neighbours = 2
        app.gui.setvar(group, "subgrid_loaded", False)
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

        self.subgrid_file = None
        self.dsa = None

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

    def _set_cell_layout(self, near_file: str) -> bool:
        """Give the flood map the (n, m) position of every cell, for 2-D map output.

        Taken from the active SFINCS (hydromt) model when one is loaded,
        otherwise from ``sfincs.nc`` next to ``near_file``.
        """
        model = app.active_model
        grid = None
        if model is not None and model.name == "sfincs_hmt":
            try:
                grid = model.domain.quadtree_grid.data
                if grid is None or len(grid.data_vars) == 0:
                    grid = None
            except Exception:
                grid = None
        if grid is not None:
            self.flood_map.set_cell_layout(grid["n"].to_numpy(), grid["m"].to_numpy())
            return True
        grid_file = os.path.join(os.path.dirname(near_file), "sfincs.nc")
        if os.path.exists(grid_file):
            with xr.open_dataset(grid_file) as g:
                self.flood_map.set_cell_layout(g["n"].to_numpy(), g["m"].to_numpy())
            return True
        return False

    def _cell_geometry(self, subgrid_file: str):
        """Return cell centres and areas of the quadtree grid.

        Taken from the active SFINCS (hydromt) model when one is loaded,
        otherwise from ``sfincs.nc`` next to the subgrid file.

        Parameters
        ----------
        subgrid_file : str
            Path of the subgrid file, used to locate a grid file.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            Cell centre x, cell centre y and cell area (m2).
        """
        model = app.active_model
        grid = None
        if model is not None and model.name == "sfincs_hmt":
            try:
                grid = model.domain.quadtree_grid.data
                if grid is None or len(grid.data_vars) == 0:
                    grid = None
            except Exception:
                grid = None

        if grid is not None:
            xy = grid.grid.face_coordinates
            xc, yc = xy[:, 0], xy[:, 1]
            level = grid["level"].to_numpy() - 1
            dx = float(grid.attrs["dx"])
            dy = float(grid.attrs["dy"])
        else:
            grid_file = os.path.join(os.path.dirname(subgrid_file), "sfincs.nc")
            if not os.path.exists(grid_file):
                raise FileNotFoundError(
                    "No SFINCS quadtree model loaded and no sfincs.nc found next to "
                    "the subgrid file; cell centres and areas are needed."
                )
            with xr.open_dataset(grid_file) as g:
                xc = g["mesh2d_face_x"].to_numpy()
                yc = g["mesh2d_face_y"].to_numpy()
                level = g["level"].to_numpy() - 1
                dx = float(g.attrs["dx"])
                dy = float(g.attrs["dy"])
        area = (dx / 2**level) * (dy / 2**level)
        return xc, yc, area

    def _model_structures(self):
        """Thin dams and weirs of the active SFINCS (hydromt) model as linestrings.

        Returns
        -------
        list
            Shapely geometries in the model CRS (empty when none or no model).
        """
        model = app.active_model
        if model is None or model.name != "sfincs_hmt":
            return []
        lines = []
        for name in ("thin_dams", "weirs"):
            try:
                gdf = getattr(model.domain, name).data
            except Exception:
                continue
            if gdf is None or len(gdf) == 0:
                continue
            lines.extend(g for g in gdf.geometry if g is not None and not g.is_empty)
        return lines

    def apply_structures_to_index(self) -> None:
        """Write a structure-aware copy of the loaded index GeoTIFF and use it."""
        from hydromt_sfincs.workflows.flood_map import apply_structures_to_index_cog

        if not getattr(self, "index_geotiff", None):
            app.gui.window.dialog_warning("Load or generate an index GeoTiff first.")
            return
        lines = self._model_structures()
        if not lines:
            app.gui.window.dialog_warning(
                "The active model has no thin dams or weirs to apply."
            )
            return
        full_name, path, name, ext, fltr = app.gui.window.dialog_save_file(
            "Save structure-aware index geotiff file", filter="*.tif"
        )
        if not full_name:
            return
        wb = app.gui.window.dialog_wait("Applying structures to index ...")
        try:
            xc, yc, area = self._cell_geometry(self.index_geotiff)
            n = apply_structures_to_index_cog(self.index_geotiff, full_name, lines, xc, yc)
            self.index_geotiff = full_name
            self.flood_map.set_index_file(full_name)  # picks up the stored structures
            app.gui.setvar(
                "flood_map", "index_file_string", f"File : {os.path.basename(full_name)}"
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            wb.close()
            app.gui.window.dialog_warning(f"Error applying structures:\n{e}")
            return
        wb.close()
        app.gui.window.dialog_info(f"{n} pixels reassigned across structures.")

    def load_subgrid_file(self) -> None:
        """Select and load a subgrid file (with residual tables) via dialog."""
        full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
            "Select subgrid file", filter="*.nc"
        )
        if not full_name:
            return
        try:
            xc, yc, area = self._cell_geometry(full_name)
            self.flood_map.set_subgrid(full_name, xc, yc, area)
            # Exact volume inversion on the raster pixels; keep a horizontal
            # surface in cells touching the sea and in non-planar cells.
            self.flood_map.set_slope_options(
                slope_zmin=0.0,
                max_residual_relief=float(
                    app.gui.getvar("flood_map", "max_residual_relief")
                ),
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            app.gui.window.dialog_warning(f"Error loading subgrid file:\n{e}")
            return
        self.subgrid_file = full_name
        app.gui.setvar("flood_map", "subgrid_loaded", True)
        # set_subgrid() switches to "slope"; keep the method the user selected
        self.flood_map.set_method(app.gui.getvar("flood_map", "flood_map_method"))

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
            n_reassigned = 0
            if model.name == "sfincs_hmt":
                # includes the model's thin dams and weirs (structure-aware index)
                n_reassigned = grid.create_index_cog(
                    full_name, app.toolbox["flood_map"].topobathy_geotiff
                )
            else:
                grid.make_index_cog(
                    full_name, app.toolbox["flood_map"].topobathy_geotiff
                )
            self.flood_map.set_index_file(full_name)
            self.index_geotiff = full_name
            app.gui.setvar(
                "flood_map", "index_file_string", f"File : {os.path.basename(full_name)}"
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            wb.close()
            app.gui.window.dialog_warning(f"Error generating index:\n{e}")
            return
        wb.close()
        if n_reassigned:
            app.gui.window.dialog_info(
                f"Index includes the model's structures: {n_reassigned} pixels "
                "reassigned across thin dams and weirs."
            )

    def load_map_output(self) -> None:
        """Load model map output from a NetCDF file."""
        file_name = app.gui.window.dialog_open_file("Open map output file", "*.nc")
        # Use full path
        if file_name[0]:
            # Read the map output
            self.map_file_name = file_name[0]

            self.dsa = xr.open_dataset(self.map_file_name)

            # Regular grids and single-level quadtrees write 2-D (n, m) output;
            # the flood map needs the cell layout to map it to the index raster
            if "zsmax" in self.dsa and self.dsa["zsmax"].ndim == 3:
                if not self._set_cell_layout(self.map_file_name):
                    app.gui.window.dialog_warning(
                        "Map output is 2-D but no model grid was found to map it; "
                        "load the model or put sfincs.nc next to the map file."
                    )

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

        # Water level, and the subgrid cell volume when the map file has it
        # (storezvolume = 1): "subgrid_volume" per output time, "zvolmax"
        # per maximum-output interval.
        if instantaneous_or_maximum == "instantaneous":
            zs = self.dsa.zs.isel(time=itime).values[:]
            volume = None
            if "subgrid_volume" in self.dsa:
                volume = self.dsa.subgrid_volume.isel(time=itime).values[:]
        else:
            zs = self.dsa.zsmax.isel(timemax=itime).values[:]
            volume = None
            if "zvolmax" in self.dsa:
                volume = self.dsa.zvolmax.isel(timemax=itime).values[:]

        self.flood_map.set_water_level(zs)
        self.flood_map.set_volume(volume)

        method = app.gui.getvar("flood_map", "flood_map_method")
        if method == "slope" and self.flood_map.subgrid is None:
            app.gui.window.dialog_warning(
                "Load a subgrid file (with z_level_res tables) to use the slope method."
            )
            method = "level"
            app.gui.setvar("flood_map", "flood_map_method", method)
        self.flood_map.set_method(method)
        try:
            max_jump = float(app.gui.getvar("flood_map", "max_jump"))
        except (TypeError, ValueError):
            max_jump = 1.0
            app.gui.setvar("flood_map", "max_jump", max_jump)
        try:
            max_relief = float(app.gui.getvar("flood_map", "max_residual_relief"))
        except (TypeError, ValueError):
            max_relief = 10.0
            app.gui.setvar("flood_map", "max_residual_relief", max_relief)
        self.flood_map.set_slope_options(
            blend=True,
            max_jump=max_jump,
            max_residual_relief=max_relief,
            flat_level_rule=True,
            flat_level_ratio=self.flat_level_ratio,
            flat_level_min_neighbours=self.flat_level_min_neighbours,
        )

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
