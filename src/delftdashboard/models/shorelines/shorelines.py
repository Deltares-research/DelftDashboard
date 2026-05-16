import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import CRS
from shapely.geometry import LineString, MultiLineString, Point, box

import delftdashboard.operations.model
from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.models.shorelines.domain import (
    coastline_created,
    coastline_modified,
    coastline_selected,
)
from delftdashboard.models.shorelines.dunes import dune_selected_from_map
from delftdashboard.models.shorelines.nourishments import (
    nourishments_created,
    nourishments_modified,
    nourishments_selected,
)
from delftdashboard.models.shorelines.structures import (
    revetments_created,
    revetments_modified,
    revetments_selected,
    structures_created,
    structures_modified,
    structures_selected,
)

try:
    from cht_shorelines import Shorelines
except ImportError:  # pragma: no cover - handled at runtime in initialize
    Shorelines = None


_MODEL = "shorelines"


class Model(delftdashboard.operations.model.GenericModel):
    name = _MODEL
    long_name = "ShorelineS"

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.long_name = "ShorelineS"

    def initialize(self):
        self.clear_layers()
        self.path = os.getcwd()
        self.runfile = "shorelines.txt"
        self.domain = self._new_domain(self.path, self.runfile)
        epsg = app.crs.to_epsg()
        if epsg is not None:
            self.domain.input.variables.epsg = epsg

        self.coastline_gdf = self._empty_gdf()
        self.structures_gdf = self._empty_gdf()
        self.revetments_gdf = self._empty_gdf()
        self.dunes_gdf = self._empty_dune_gdf()
        self.nourishments_gdf = self._empty_gdf(
            {
                "tstart": pd.Series(dtype="float64"),
                "tend": pd.Series(dtype="float64"),
                "totalvolume": pd.Series(dtype="float64"),
            }
        )
        self.nourishment_geometry_mode = "nor"
        self.polygon_nourishment_file = ""
        self.selected_feature = {}
        self.set_gui_variables()

    def _new_domain(self, root, runfile):
        if Shorelines is None:
            raise ImportError(
                "The cht_shorelines package is required for ShorelineS model setup."
            )
        return Shorelines(root=root, crs=app.crs, runfile=runfile)

    def add_layers(self):
        layer = app.map.add_layer(_MODEL)
        layer.add_layer(
            "coastline",
            type="draw",
            shape="polyline",
            create=coastline_created,
            modify=coastline_modified,
            select=coastline_selected,
            polyline_line_color="#ffcc00",
            polyline_line_width=4,
        )
        layer.add_layer(
            "structures",
            type="draw",
            shape="polyline",
            create=structures_created,
            modify=structures_modified,
            select=structures_selected,
            polyline_line_color="#e11d48",
            polyline_line_width=4,
        )
        layer.add_layer(
            "revetments",
            type="draw",
            shape="polyline",
            create=revetments_created,
            modify=revetments_modified,
            select=revetments_selected,
            polyline_line_color="#9333ea",
            polyline_line_width=4,
        )
        layer.add_layer(
            "nourishments",
            type="draw",
            shape="polyline",
            create=nourishments_created,
            modify=nourishments_modified,
            select=nourishments_selected,
            polyline_line_color="#16a34a",
            polyline_line_width=5,
        )
        layer.add_layer(
            "dunes",
            type="circle_selector",
            select=dune_selected_from_map,
            line_color="white",
            line_opacity=1.0,
            fill_color="#f97316",
            fill_opacity=1.0,
            circle_radius=5,
            circle_radius_selected=6,
            line_color_selected="white",
            fill_color_selected="#dc2626",
            circle_radius_inactive=5,
            line_color_inactive="white",
            fill_color_inactive="lightgrey",
        )

    def set_layer_mode(self, mode):
        if _MODEL not in app.map.layer:
            return
        for name in ["coastline", "structures", "revetments", "nourishments", "dunes"]:
            draw_layer = app.map.layer[_MODEL].layer[name]
            if mode == "inactive":
                draw_layer.deactivate()
            elif mode == "invisible":
                draw_layer.hide()

    def set_crs(self):
        if self.domain is None:
            return
        if app.crs == self.domain.crs:
            return

        old_crs = self.domain.crs
        self.domain.crs = app.crs
        for attr in [
            "coastline_gdf",
            "structures_gdf",
            "revetments_gdf",
            "dunes_gdf",
            "nourishments_gdf",
        ]:
            gdf = getattr(self, attr)
            if len(gdf.index) == 0:
                setattr(self, attr, self._empty_like(gdf))
            elif gdf.crs is None:
                setattr(self, attr, gdf.set_crs(old_crs).to_crs(app.crs))
            else:
                setattr(self, attr, gdf.to_crs(app.crs))
        self.plot()

    def open(self):
        filename = app.gui.window.dialog_open_file(
            "Select ShorelineS input file",
            filter="Input files (*.txt *.inp);;All files (*)",
        )
        if not filename:
            return
        if isinstance(filename, (list, tuple)):
            filename = filename[0]

        dlg = app.gui.window.dialog_wait("Loading ShorelineS model ...")
        try:
            self._set_case_file(filename)
            os.chdir(self.path)

            self.domain = self._new_domain(self.path, self.runfile)
            self.domain.read()

            saved_epsg = getattr(self.domain.input.variables, "epsg", None)
            if saved_epsg not in (None, ""):
                self.domain.crs = CRS.from_user_input(saved_epsg)
                map.set_crs(self.domain.crs)

            self._load_attribute_files()
            self.set_gui_variables()
            self.plot()
            self.zoom_to_model()
            app.gui.window.update()
        finally:
            dlg.close()

    def save(self):
        self.set_model_variables()
        self._sync_domain_path()
        self.domain.crs = app.crs
        epsg = app.crs.to_epsg()
        if epsg is not None:
            self.domain.input.variables.epsg = epsg
        self._sync_geometry_to_domain()
        self.domain.write()
        self.domain.write_matlab_runner()
        app.gui.window.update()

    def save_setup(self):
        filename = self._get_save_setup_filename()
        if filename is None:
            return

        self._set_case_file(filename)
        os.chdir(self.path)
        app.gui.setvar(_MODEL, "runfile", self.runfile)
        self.save()

    def save_feature(self, layer_name):
        """Write a drawn feature layer to its ShorelineS attribute file."""
        self.set_model_variables()
        self._sync_domain_path()
        self.domain.crs = app.crs
        epsg = app.crs.to_epsg()
        if epsg is not None:
            self.domain.input.variables.epsg = epsg
        variables = self.domain.input.variables

        if layer_name == "coastline":
            sections = self._sections_from_gdf(self.coastline_gdf)
            if not sections:
                self._clear_domain_feature("coastline")
                app.gui.setvar(_MODEL, "ldbcoastline", "")
                self.domain.input.write()
                app.gui.window.update()
                return
            file_name = (
                self._get_gui("ldbcoastline", variables.ldbcoastline)
                or "coastline.ldb"
            )
            self.domain.grid.set_coastline(sections, file_name=file_name)
            self.domain.grid.write()
            app.gui.setvar(_MODEL, "ldbcoastline", file_name)

        elif layer_name == "structures":
            sections = self._sections_from_gdf(self.structures_gdf)
            if not sections:
                self._clear_domain_feature("structures")
                app.gui.setvar(_MODEL, "ldbstructures", "")
                self.domain.input.write()
                app.gui.window.update()
                return
            file_name = (
                self._get_gui("ldbstructures", variables.ldbstructures)
                or "structures.ldb"
            )
            self.domain.structures.set_structures(sections, file_name=file_name)
            self.domain.structures.write()
            app.gui.setvar(_MODEL, "ldbstructures", file_name)

        elif layer_name == "revetments":
            sections = self._sections_from_gdf(self.revetments_gdf)
            if not sections:
                self._clear_domain_feature("revetments")
                app.gui.setvar(_MODEL, "ldbrevetments", "")
                self.domain.input.write()
                app.gui.window.update()
                return
            file_name = (
                self._get_gui("ldbrevetments", variables.ldbrevetments)
                or "revetments.ldb"
            )
            self.domain.structures.set_revetments(sections, file_name=file_name)
            self.domain.structures.write()
            app.gui.setvar(_MODEL, "ldbrevetments", file_name)

        elif layer_name == "nourishments":
            file_name = self._sync_nourishments_to_domain()
            if not file_name:
                app.gui.setvar(_MODEL, "norfile", "")
                self.domain.input.write()
                app.gui.window.update()
                return
            self.domain.write_attribute_files()
            app.gui.setvar(_MODEL, "norfile", file_name)

        elif layer_name == "dunes":
            file_name = self._sync_dunes_to_domain()
            if not file_name:
                app.gui.setvar(_MODEL, "ldbdune", "")
                self.domain.input.write()
                app.gui.window.update()
                return
            self.domain.write_attribute_files()
            app.gui.setvar(_MODEL, "ldbdune", file_name)

        else:
            raise ValueError(f"Unknown ShorelineS feature layer: {layer_name}")

        self.domain.input.write()
        app.gui.window.update()

    def plot(self):
        if _MODEL not in app.map.layer:
            return
        for name in ["coastline", "structures", "revetments", "nourishments"]:
            app.map.layer[_MODEL].layer[name].set_data(getattr(self, f"{name}_gdf"))
        active_dune = self._get_gui("active_dunes", 0)
        app.map.layer[_MODEL].layer["dunes"].set_data(self.dunes_gdf, active_dune)
        app.gui.window.update()

    def zoom_to_model(self):
        bounds = self._total_bounds()
        if bounds is None:
            return
        bbox = gpd.GeoDataFrame(geometry=[box(*bounds)], crs=app.crs).to_crs(4326)
        b = bbox.total_bounds
        app.map.zoom_to_extent([b[0], b[2]], [b[1], b[3]])

    def set_gui_variables(self):
        app.gui.setvar(_MODEL, "runfile", self.runfile)
        app.gui.setvar(_MODEL, "wave_input_type", "constant")
        app.gui.setvar(_MODEL, "active_coastline", 0)
        app.gui.setvar(_MODEL, "active_structures", 0)
        app.gui.setvar(_MODEL, "active_revetments", 0)
        app.gui.setvar(_MODEL, "active_dunes", 0)
        app.gui.setvar(_MODEL, "active_nourishments", 0)
        app.gui.setvar(_MODEL, "nourishment_tstart", 20200101)
        app.gui.setvar(_MODEL, "nourishment_tend", 20400101)
        app.gui.setvar(_MODEL, "nourishment_totalvolume", 100000.0)

        variables = self.domain.input.variables
        for name, value in vars(variables).items():
            app.gui.setvar(_MODEL, name, self._value_for_gui(value))
        wave_input_type = self._infer_wave_input_type(variables)
        app.gui.setvar(_MODEL, "wave_input_type", wave_input_type)
        if not variables.wvcfile and variables.waveclimfile:
            app.gui.setvar(_MODEL, "wvcfile", variables.waveclimfile)
        if self.nourishment_geometry_mode == "polygon" and self.polygon_nourishment_file:
            app.gui.setvar(_MODEL, "norfile", self.polygon_nourishment_file)

        self._set_list_vars()
        self._set_dune_editor_fields()

    def set_model_variables(self):
        self.runfile = self._get_gui("runfile", self.runfile)
        self.domain.input.runfile = self.runfile

        variables = self.domain.input.variables
        for name, current in vars(variables).items():
            setattr(
                variables,
                name,
                self._coerce_like(self._get_gui(name, current), current),
            )

        wave_input_type = self._get_gui("wave_input_type", "constant")
        if wave_input_type == "constant":
            variables.wvcfile = ""
            variables.waveclimfile = ""
        else:
            wave_file = self._get_gui(
                "wvcfile",
                variables.wvcfile or variables.waveclimfile,
            )
            variables.wvcfile = wave_file
            variables.waveclimfile = wave_file if wave_input_type == "climate" else ""
        if self.nourishment_geometry_mode == "polygon":
            self.polygon_nourishment_file = self._get_gui(
                "norfile",
                self.polygon_nourishment_file,
            )

    def select_layer(self, layer_name):
        app.map.layer[_MODEL].layer[layer_name].activate()
        app.gui.window.update()

    def draw_feature(self, layer_name):
        app.map.layer[_MODEL].layer[layer_name].draw()

    def delete_feature(self, layer_name):
        if layer_name == "dunes":
            self.delete_dune()
            return
        gdf = getattr(self, f"{layer_name}_gdf")
        index = self.selected_feature.get(layer_name)
        if index is None or index not in gdf.index:
            return
        setattr(self, f"{layer_name}_gdf", gdf.drop(index=index).reset_index(drop=True))
        self.selected_feature[layer_name] = None
        self._set_list_vars()
        self.plot()

    def feature_created(self, layer_name, gdf, index=None, feature_id=None):
        self._store_draw_layer(layer_name, gdf)

    def feature_modified(self, layer_name, gdf, index=None, feature_id=None):
        self._store_draw_layer(layer_name, gdf)

    def feature_selected(self, layer_name, gdf, index=None, feature_id=None):
        self.selected_feature[layer_name] = index
        app.gui.setvar(_MODEL, f"active_{layer_name}", 0 if index is None else int(index))
        app.gui.window.update()

    def load_xy_feature(self, layer_name):
        filename = app.gui.window.dialog_open_file(
            f"Select {layer_name} file",
            filter="XY files (*.ldb *.xy *.nor *.dun *.txt);;All files (*)",
        )
        if not filename:
            return
        if isinstance(filename, (list, tuple)):
            filename = filename[0]
        if not filename:
            return
        if layer_name == "nourishments" and self._looks_like_nourishment_file(filename):
            gdf = self._load_optional_nourishments(filename)
            self.nourishment_geometry_mode = "nor"
            self.polygon_nourishment_file = ""
        elif layer_name == "nourishments":
            gdf = self._load_polygon_nourishments(filename)
            self.nourishment_geometry_mode = "polygon"
            self.polygon_nourishment_file = str(Path(filename).name)
        elif layer_name == "dunes":
            gdf = self._load_optional_dunes(filename)
        else:
            gdf = self._gdf_from_xy_file(filename)
        setattr(self, f"{layer_name}_gdf", gdf)
        self._set_list_vars()
        if layer_name == "dunes":
            self._set_dune_editor_fields(0 if len(gdf.index) else None)
        self.plot()

    def _sync_domain_path(self):
        current_path = self.path or getattr(self.domain, "path", None) or os.getcwd()
        self.path = str(Path(current_path))
        self.domain.path = self.path
        self.domain.input.root = Path(self.path)
        self.domain.input.runfile = self.runfile

    def _sync_geometry_to_domain(self):
        variables = self.domain.input.variables

        coastline_file = self._get_gui("ldbcoastline", variables.ldbcoastline) or "coastline.ldb"
        coastline = self._sections_from_gdf(self.coastline_gdf)
        if coastline:
            self.domain.grid.set_coastline(coastline, file_name=coastline_file)
        else:
            self._clear_domain_feature("coastline")

        structures = self._sections_from_gdf(self.structures_gdf)
        if structures:
            self.domain.structures.set_structures(
                structures,
                file_name=self._get_gui("ldbstructures", variables.ldbstructures) or "structures.ldb",
            )
        else:
            self._clear_domain_feature("structures")

        revetments = self._sections_from_gdf(self.revetments_gdf)
        if revetments:
            self.domain.structures.set_revetments(
                revetments,
                file_name=self._get_gui("ldbrevetments", variables.ldbrevetments) or "revetments.ldb",
            )
        else:
            self._clear_domain_feature("revetments")

        self._sync_dunes_to_domain()
        self._sync_nourishments_to_domain()

    def _load_attribute_files(self):
        variables = self.domain.input.variables
        self.coastline_gdf = self._load_optional_xy(variables.ldbcoastline)
        self.structures_gdf = self._load_optional_xy(variables.ldbstructures)
        self.revetments_gdf = self._load_optional_xy(variables.ldbrevetments)
        self.dunes_gdf = self._load_optional_dunes(getattr(variables, "ldbdune", ""))
        if variables.norfile:
            self.nourishments_gdf = self._load_optional_nourishments(variables.norfile)
            self.nourishment_geometry_mode = "nor"
            self.polygon_nourishment_file = ""
        elif getattr(variables, "ldbnourish", ""):
            ldbnourish = variables.ldbnourish
            if str(ldbnourish).lower().endswith(".nor"):
                self.nourishments_gdf = self._load_optional_nourishments(ldbnourish)
                self.nourishment_geometry_mode = "nor"
                self.polygon_nourishment_file = ""
            else:
                self.nourishments_gdf = self._load_polygon_nourishments(ldbnourish)
                self.nourishment_geometry_mode = "polygon"
                self.polygon_nourishment_file = str(Path(ldbnourish).name)
        else:
            self.nourishments_gdf = self._empty_gdf(
                {
                    "tstart": pd.Series(dtype="float64"),
                    "tend": pd.Series(dtype="float64"),
                    "totalvolume": pd.Series(dtype="float64"),
                }
            )
            self.nourishment_geometry_mode = "nor"
            self.polygon_nourishment_file = ""
        self._set_list_vars()
        self._set_dune_editor_fields(0 if len(self.dunes_gdf.index) else None)

    def _load_optional_xy(self, file_name):
        if not file_name:
            return self._empty_gdf()
        path = Path(self.path) / file_name
        if not path.exists():
            return self._empty_gdf()
        return self._gdf_from_xy_file(path)

    def _load_optional_dunes(self, file_name):
        if not file_name:
            return self._empty_dune_gdf()
        path = Path(file_name)
        if not path.is_absolute():
            path = Path(self.path) / file_name
        if not path.exists():
            return self._empty_dune_gdf()

        data = np.loadtxt(path, ndmin=2)
        if data.size == 0:
            return self._empty_dune_gdf()
        if data.ndim == 1:
            data = data.reshape(1, -1)

        columns = ["wberm", "dfelev", "dcelev", "cs", "cstill", "xtill", "perctill"]
        records = []
        for row in data:
            if len(row) < 5:
                continue
            values = [np.nan] * len(columns)
            for index, value in enumerate(row[2 : 2 + len(columns)]):
                values[index] = float(value)
            record = dict(zip(columns, values))
            record["geometry"] = Point(float(row[0]), float(row[1]))
            records.append(record)
        if not records:
            return self._empty_dune_gdf()
        return gpd.GeoDataFrame(records, crs=app.crs)

    def _load_optional_nourishments(self, file_name):
        if not file_name:
            return self._empty_gdf(
                {
                    "tstart": pd.Series(dtype="float64"),
                    "tend": pd.Series(dtype="float64"),
                    "totalvolume": pd.Series(dtype="float64"),
                }
            )
        path = Path(file_name)
        if not path.is_absolute():
            path = Path(self.path) / file_name
        if not path.exists():
            return self._empty_gdf(
                {
                    "tstart": pd.Series(dtype="float64"),
                    "tend": pd.Series(dtype="float64"),
                    "totalvolume": pd.Series(dtype="float64"),
                }
            )

        data = np.loadtxt(path, ndmin=2)
        records = []
        for row in data:
            if len(row) < 7:
                continue
            records.append(
                {
                    "tstart": row[4],
                    "tend": row[5],
                    "totalvolume": row[6],
                    "geometry": LineString([(row[0], row[1]), (row[2], row[3])]),
                }
            )
        if not records:
            return self._empty_gdf(
                {
                    "tstart": pd.Series(dtype="float64"),
                    "tend": pd.Series(dtype="float64"),
                    "totalvolume": pd.Series(dtype="float64"),
                }
            )
        return gpd.GeoDataFrame(records, crs=app.crs)

    def _load_polygon_nourishments(self, file_name):
        path = Path(file_name)
        if not path.is_absolute():
            path = Path(self.path) / file_name
        if not path.exists():
            return self._empty_gdf(
                {
                    "tstart": pd.Series(dtype="float64"),
                    "tend": pd.Series(dtype="float64"),
                    "totalvolume": pd.Series(dtype="float64"),
                }
            )

        sections = self._gdf_from_xy_file(path)
        variables = self.domain.input.variables
        default_tstart = self._coerce_to_yyyymmdd(variables.reftime, 20200101)
        default_tend = self._coerce_to_yyyymmdd(variables.endofsimulation, 20400101)
        default_rate = self._as_float(getattr(variables, "nourrate", 0.0), 0.0)
        tstarts = self._read_nourishment_dates(getattr(variables, "nourstartfile", ""))
        tends = self._read_nourishment_dates(getattr(variables, "nourendfile", ""))
        rates = self._read_numeric_vector(getattr(variables, "nourratefile", ""))

        records = []
        for index, geometry in enumerate(sections.geometry):
            tstart = self._value_for_index(tstarts, index, default_tstart)
            tend = self._value_for_index(tends, index, default_tend)
            rate = self._value_for_index(rates, index, default_rate)
            records.append(
                {
                    "tstart": tstart,
                    "tend": tend,
                    "totalvolume": self._rate_to_totalvolume(rate, tstart, tend),
                    "geometry": geometry,
                }
            )
        return gpd.GeoDataFrame(records, crs=app.crs)

    def _looks_like_nourishment_file(self, filename):
        try:
            data = np.loadtxt(filename, ndmin=2)
        except Exception:
            return False
        return data.ndim == 2 and data.shape[1] >= 7

    def _store_draw_layer(self, layer_name, gdf):
        if gdf is None:
            gdf = self._empty_gdf()
        if gdf.crs is None:
            gdf = gdf.set_crs(app.crs)
        setattr(self, f"{layer_name}_gdf", gdf.reset_index(drop=True))
        self._set_list_vars()
        if layer_name == "dunes":
            self._set_dune_editor_fields(0 if len(gdf.index) else None)
        app.gui.window.update()

    def _set_list_vars(self):
        for name in ["coastline", "structures", "revetments", "dunes", "nourishments"]:
            gdf = getattr(self, f"{name}_gdf")
            values = [f"{name[:-1] if name.endswith('s') else name} {i + 1}" for i in range(len(gdf.index))]
            app.gui.setvar(_MODEL, f"{name}_names", values)
            app.gui.setvar(_MODEL, f"nr_{name}", len(values))

    def _sections_from_gdf(self, gdf):
        sections = []
        if gdf is None or len(gdf.index) == 0:
            return sections
        work = gdf if gdf.crs is not None else gdf.set_crs(app.crs)
        if work.crs != self.domain.crs:
            work = work.to_crs(self.domain.crs)
        for geom in work.geometry:
            for line in self._iter_lines(geom):
                xy = np.asarray(line.coords, dtype=float)[:, :2]
                if len(xy) >= 2:
                    sections.append(xy)
        return sections

    def _nourishments_from_gdf(self):
        records = []
        if self.nourishments_gdf is None or len(self.nourishments_gdf.index) == 0:
            return records
        work = self.nourishments_gdf
        if work.crs is None:
            work = work.set_crs(app.crs)
        if work.crs != self.domain.crs:
            work = work.to_crs(self.domain.crs)

        default_tstart = self._as_date_int(self._get_gui("nourishment_tstart", 20200101), 20200101)
        default_tend = self._as_date_int(self._get_gui("nourishment_tend", 20400101), 20400101)
        default_volume = self._as_float(
            self._get_gui("nourishment_totalvolume", 100000.0), 100000.0
        )
        for _, row in work.iterrows():
            for line in self._iter_lines(row.geometry):
                coords = list(line.coords)
                if len(coords) < 2:
                    continue
                records.append(
                    {
                        "tstart": self._as_date_int(row.get("tstart", default_tstart), default_tstart),
                        "tend": self._as_date_int(row.get("tend", default_tend), default_tend),
                        "totalvolume": self._as_float(
                            row.get("totalvolume", default_volume), default_volume
                        ),
                        "xstart": coords[0][0],
                        "ystart": coords[0][1],
                        "xend": coords[-1][0],
                        "yend": coords[-1][1],
                    }
                )
        return records

    def _gdf_from_xy_file(self, filename):
        data = np.loadtxt(filename, ndmin=2)
        sections = []
        points = []
        for row in data:
            if len(row) < 2 or np.any(np.isnan(row[:2])):
                if len(points) >= 2:
                    sections.append(LineString(points))
                points = []
                continue
            points.append((row[0], row[1]))
        if len(points) >= 2:
            sections.append(LineString(points))
        return gpd.GeoDataFrame(geometry=sections, crs=app.crs)

    def _total_bounds(self):
        bounds = []
        for attr in [
            "coastline_gdf",
            "structures_gdf",
            "revetments_gdf",
            "dunes_gdf",
            "nourishments_gdf",
        ]:
            gdf = getattr(self, attr)
            if gdf is not None and len(gdf.index) > 0:
                bounds.append(gdf.total_bounds)
        if not bounds:
            return None
        bounds = np.asarray(bounds)
        return [
            np.nanmin(bounds[:, 0]),
            np.nanmin(bounds[:, 1]),
            np.nanmax(bounds[:, 2]),
            np.nanmax(bounds[:, 3]),
        ]

    def _empty_gdf(self, columns=None):
        data = columns or {}
        return gpd.GeoDataFrame(data, geometry=[], crs=app.crs)

    def _empty_dune_gdf(self):
        return self._empty_gdf(
            {
                "wberm": pd.Series(dtype="float64"),
                "dfelev": pd.Series(dtype="float64"),
                "dcelev": pd.Series(dtype="float64"),
                "cs": pd.Series(dtype="float64"),
                "cstill": pd.Series(dtype="float64"),
                "xtill": pd.Series(dtype="float64"),
                "perctill": pd.Series(dtype="float64"),
            }
        )

    def _empty_like(self, gdf):
        columns = {col: pd.Series(dtype=gdf[col].dtype) for col in gdf.columns if col != "geometry"}
        return self._empty_gdf(columns)

    def _iter_lines(self, geometry):
        if geometry is None or geometry.is_empty:
            return
        if isinstance(geometry, LineString):
            yield geometry
        elif isinstance(geometry, MultiLineString):
            yield from geometry.geoms

    def _get_gui(self, name, default=None):
        try:
            return app.gui.getvar(_MODEL, name)
        except Exception:
            return default

    def _set_case_file(self, filename):
        path = Path(filename)
        self.path = str(path.parent)
        self.runfile = path.name

    def _get_save_setup_filename(self):
        response = app.gui.window.dialog_save_file(
            "Save ShorelineS input file",
            file_name=self.runfile,
            filter="Input files (*.txt *.inp);;All files (*)",
        )
        if response[0]:
            return response[2]
        return None

    def _value_for_gui(self, value):
        if value is None:
            return ""
        return value

    def _coerce_like(self, value, current):
        if isinstance(current, bool):
            return self._as_bool(value)
        if isinstance(current, int) and not isinstance(current, bool):
            return int(self._as_float(value, current))
        if isinstance(current, float):
            return self._as_float(value, current)
        if isinstance(current, list):
            return self._coerce_sequence(value)
        return value

    def _coerce_sequence(self, value):
        if isinstance(value, (list, tuple)):
            return list(value)
        if value is None:
            return []
        text = str(value).strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()
        if text.startswith("{") and text.endswith("}"):
            text = text[1:-1].strip()
        rows = [row.strip() for row in text.replace(",", " ").split(";") if row.strip()]
        values = []
        for row in rows:
            parsed_row = [self._parse_sequence_token(token) for token in row.split()]
            if parsed_row:
                values.append(parsed_row)
        if not values:
            return []
        if len(values) == 1:
            return values[0]
        return values

    def _parse_sequence_token(self, token):
        text = str(token).strip().strip("'\"")
        try:
            value = float(text)
        except ValueError:
            return text
        if value.is_integer() and "e" not in text.lower() and "." not in text:
            return int(value)
        return value

    def _as_float(self, value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _coerce_to_yyyymmdd(self, value, default):
        text = str(value).strip()
        if text.endswith(".0"):
            text = text[:-2]
        if text.isdigit() and len(text) == 8:
            return int(text)
        try:
            return int(pd.Timestamp(value).strftime("%Y%m%d"))
        except (TypeError, ValueError):
            return default

    def _as_date_int(self, value, default):
        return self._coerce_to_yyyymmdd(value, default)

    def _as_bool(self, value):
        if isinstance(value, str):
            return value.strip().lower() in ["1", "true", "yes", "on"]
        return bool(value)

    def _infer_wave_input_type(self, variables):
        wave_file = variables.wvcfile or getattr(variables, "waveclimfile", "")
        if not wave_file:
            return "constant"
        wave_boundary_conditions = getattr(self.domain, "wave_boundary_conditions", None)
        if wave_boundary_conditions is not None:
            if (
                wave_boundary_conditions.wave_timeseries
                or wave_boundary_conditions.spatial_wave_points
                or wave_boundary_conditions.spatial_wave_file
            ):
                return "timeseries"
            if wave_boundary_conditions.wave_climate is not None:
                return "climate"
        if Path(str(wave_file)).suffix.lower() in {".wvt", ".wvd", ".wlt", ".wdt"}:
            return "timeseries"
        return "climate"

    def _clear_domain_feature(self, layer_name):
        variables = self.domain.input.variables
        if layer_name == "coastline":
            self.domain.grid.coastline = None
            self.domain.grid.coastline_file = None
            variables.ldbcoastline = ""
            variables.xmc = ""
            variables.ymc = ""
            return
        if layer_name == "structures":
            self.domain.structures.structures = None
            self.domain.structures.structures_file = None
            variables.ldbstructures = ""
            variables.xhard = []
            variables.yhard = []
            variables.struct = 0
            return
        if layer_name == "revetments":
            self.domain.structures.revetments = None
            self.domain.structures.revetments_file = None
            variables.ldbrevetments = ""
            variables.xrevet = []
            variables.yrevet = []
            variables.revet = 0
            return
        if layer_name == "dunes":
            self.domain.initial_conditions.dunes = None
            self.domain.initial_conditions.dune_file = None
            variables.ldbdune = ""
            variables.dune = 0
            variables.xdune = 0
            variables.ydune = 0
            return
        if layer_name == "nourishments":
            self.domain.nourishments.nourishments = None
            self.domain.nourishments.nourishment_file = None
            self.domain.grid.extra_xy_files.pop("ldbnourish", None)
            variables.norfile = ""
            variables.ldbnourish = ""
            variables.nourratefile = ""
            variables.nourstartfile = ""
            variables.nourendfile = ""
            variables.nourish = 0
            self.nourishment_geometry_mode = "nor"
            self.polygon_nourishment_file = ""
            return
        raise ValueError(f"Unknown ShorelineS feature layer: {layer_name}")

    def _sync_nourishments_to_domain(self):
        variables = self.domain.input.variables
        nourishments = self._nourishments_from_gdf()
        if not nourishments:
            self._clear_domain_feature("nourishments")
            return ""

        if self.nourishment_geometry_mode == "polygon":
            sections = self._sections_from_gdf(self.nourishments_gdf)
            file_name = self.polygon_nourishment_file or "nourishments.ldb"
            self.polygon_nourishment_file = file_name
            self.domain.nourishments.nourishments = None
            self.domain.nourishments.nourishment_file = None
            self.domain.grid.set_xy_file("ldbnourish", sections, file_name=file_name)
            variables.norfile = ""
            variables.ldbnourish = file_name
            variables.nourish = 1
            self._write_polygon_nourishment_metadata(file_name, nourishments)
            return file_name

        self.domain.grid.extra_xy_files.pop("ldbnourish", None)
        variables.ldbnourish = ""
        variables.nourratefile = ""
        variables.nourstartfile = ""
        variables.nourendfile = ""
        file_name = self._get_gui("norfile", variables.norfile) or "nourishments.nor"
        self.domain.nourishments.set_nourishments(
            nourishments,
            file_name=file_name,
        )
        self.nourishment_geometry_mode = "nor"
        self.polygon_nourishment_file = ""
        return file_name

    def _sync_dunes_to_domain(self):
        variables = self.domain.input.variables
        dunes = self._dunes_from_gdf()
        if dunes.size == 0:
            self._clear_domain_feature("dunes")
            return ""

        file_name = self._get_gui("ldbdune", getattr(variables, "ldbdune", "")) or "dunes.dun"
        self.domain.dunes.set_dunes(dunes, file_name=file_name)
        variables.ldbdune = file_name
        variables.dune = 1
        return file_name

    def _write_polygon_nourishment_metadata(self, file_name, nourishments):
        path = Path(file_name)
        base_name = path.stem
        start_file = (
            self.domain.input.variables.nourstartfile or f"{base_name}_start.txt"
        )
        end_file = self.domain.input.variables.nourendfile or f"{base_name}_end.txt"
        rate_file = self.domain.input.variables.nourratefile or f"{base_name}_rate.txt"
        root = Path(self.path)

        start_lines = []
        end_lines = []
        rates = []
        for nourishment in nourishments:
            tstart = self._as_date_int(nourishment["tstart"], 20200101)
            tend = self._as_date_int(nourishment["tend"], 20400101)
            duration_days = max(
                (self._timestamp_from_yyyymmdd(tend) - self._timestamp_from_yyyymmdd(tstart)).days,
                1,
            )
            rate = float(nourishment["totalvolume"]) * 365.0 / duration_days
            start_lines.append(self._timestamp_from_yyyymmdd(tstart).strftime("%Y-%m-%d"))
            end_lines.append(self._timestamp_from_yyyymmdd(tend).strftime("%Y-%m-%d"))
            rates.append(rate)

        (root / start_file).write_text("\n".join(start_lines) + "\n", encoding="utf-8")
        (root / end_file).write_text("\n".join(end_lines) + "\n", encoding="utf-8")
        (root / rate_file).write_text(
            "\n".join(f"{rate:.6f}" for rate in rates) + "\n",
            encoding="utf-8",
        )

        self.domain.input.variables.nourstartfile = start_file
        self.domain.input.variables.nourendfile = end_file
        self.domain.input.variables.nourratefile = rate_file

    def _read_nourishment_dates(self, file_name):
        if not file_name:
            return []
        path = Path(file_name)
        if not path.is_absolute():
            path = Path(self.path) / file_name
        if not path.exists():
            return []
        values = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("%", 1)[0].strip()
            if not line:
                continue
            values.append(self._coerce_to_yyyymmdd(line, 0))
        return [value for value in values if value]

    def _read_numeric_vector(self, file_name):
        if not file_name:
            return []
        path = Path(file_name)
        if not path.is_absolute():
            path = Path(self.path) / file_name
        if not path.exists():
            return []
        data = np.loadtxt(path, ndmin=1)
        data = np.asarray(data, dtype=float).reshape(-1)
        return data.tolist()

    def _value_for_index(self, values, index, default):
        if not values:
            return default
        if index < len(values):
            return values[index]
        return values[-1]

    def _rate_to_totalvolume(self, rate, tstart, tend):
        duration_days = max(
            (
                self._timestamp_from_yyyymmdd(tend)
                - self._timestamp_from_yyyymmdd(tstart)
            ).days,
            1,
        )
        return float(rate) * duration_days / 365.0

    def _timestamp_from_yyyymmdd(self, value):
        return pd.to_datetime(str(int(value)), format="%Y%m%d")

    def load_dunes(self):
        filename = app.gui.window.dialog_open_file(
            "Select dunes file",
            filter="Dune files (*.dun *.txt);;All files (*)",
        )
        if not filename:
            return
        if isinstance(filename, tuple):
            if not filename[0]:
                return
            filename = filename[2]
        if isinstance(filename, (list, tuple)):
            filename = filename[0]
        if not filename:
            return
        self.dunes_gdf = self._load_optional_dunes(filename)
        app.gui.setvar(_MODEL, "ldbdune", Path(filename).name)
        app.gui.setvar(_MODEL, "dune", 1 if len(self.dunes_gdf.index) else 0)
        self._set_list_vars()
        self._set_dune_editor_fields(0 if len(self.dunes_gdf.index) else None)
        self.plot()

    def add_dune_point_on_map(self):
        app.map.click_point(self._dune_point_clicked)

    def _dune_point_clicked(self, x, y):
        row = self._default_dune_row(x, y)
        gdf = gpd.GeoDataFrame([row], crs=app.crs)
        if self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            self.dunes_gdf = gdf
        else:
            self.dunes_gdf = gpd.GeoDataFrame(
                pd.concat([self.dunes_gdf, gdf], ignore_index=True),
                crs=app.crs,
            )
        index = len(self.dunes_gdf.index) - 1
        app.gui.setvar(_MODEL, "active_dunes", index)
        app.gui.setvar(_MODEL, "dune", 1)
        self._set_list_vars()
        self._set_dune_editor_fields(index)
        self.plot()

    def delete_dune(self):
        if self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            return
        index = self._selected_dune_index()
        if index is None:
            return
        self.dunes_gdf = self.dunes_gdf.drop(index=index).reset_index(drop=True)
        next_index = min(index, len(self.dunes_gdf.index) - 1) if len(self.dunes_gdf.index) else None
        app.gui.setvar(_MODEL, "active_dunes", 0 if next_index is None else next_index)
        if len(self.dunes_gdf.index) == 0:
            app.gui.setvar(_MODEL, "dune", 0)
        self._set_list_vars()
        self._set_dune_editor_fields(next_index)
        self.plot()

    def select_dune_from_list(self, *args):
        if args:
            index = args[0]
            if isinstance(index, tuple):
                index = index[0]
            index = int(index)
        else:
            index = self._selected_dune_index()
        if index is None or self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            self._set_dune_editor_fields(None)
            return
        app.gui.setvar(_MODEL, "active_dunes", index)
        app.map.layer[_MODEL].layer["dunes"].select_by_index(index)
        self._set_dune_editor_fields(index)

    def select_dune_from_map(self, *args):
        index = args[0]["id"]
        app.gui.setvar(_MODEL, "active_dunes", index)
        self._set_dune_editor_fields(index)
        app.gui.window.update()

    def edit_dune_parameter(self):
        index = self._selected_dune_index()
        if index is None or self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            return
        self.dunes_gdf.at[index, "geometry"] = Point(
            self._as_float(self._get_gui("dune_x", 0.0), 0.0),
            self._as_float(self._get_gui("dune_y", 0.0), 0.0),
        )
        self.dunes_gdf.at[index, "wberm"] = self._as_float(
            self._get_gui("dune_wberm", self.domain.input.variables.wberm),
            self.domain.input.variables.wberm,
        )
        self.dunes_gdf.at[index, "dfelev"] = self._as_float(
            self._get_gui("dune_dfelev", self.domain.input.variables.dfelev),
            self.domain.input.variables.dfelev,
        )
        self.dunes_gdf.at[index, "dcelev"] = self._as_float(
            self._get_gui("dune_dcelev", self.domain.input.variables.dcelev),
            self.domain.input.variables.dcelev,
        )
        for gui_name, column_name in [
            ("dune_cs", "cs"),
            ("dune_cstill", "cstill"),
            ("dune_xtill", "xtill"),
            ("dune_perctill", "perctill"),
        ]:
            self.dunes_gdf.at[index, column_name] = self._as_optional_float(
                self._get_gui(gui_name, np.nan)
            )
        self.plot()

    def _selected_dune_index(self):
        if self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            return None
        index = self._get_gui("active_dunes", 0)
        try:
            index = int(index)
        except (TypeError, ValueError):
            index = 0
        if index < 0 or index >= len(self.dunes_gdf.index):
            return None
        return index

    def _set_dune_editor_fields(self, index=None):
        default_row = self._default_dune_row(0.0, 0.0)
        if index is not None and self.dunes_gdf is not None and index < len(self.dunes_gdf.index):
            row = self.dunes_gdf.iloc[index]
            default_row.update(
                {
                    "x": row.geometry.x,
                    "y": row.geometry.y,
                    "wberm": row.get("wberm", default_row["wberm"]),
                    "dfelev": row.get("dfelev", default_row["dfelev"]),
                    "dcelev": row.get("dcelev", default_row["dcelev"]),
                    "cs": row.get("cs", np.nan),
                    "cstill": row.get("cstill", np.nan),
                    "xtill": row.get("xtill", np.nan),
                    "perctill": row.get("perctill", np.nan),
                }
            )
            app.gui.setvar(_MODEL, "active_dunes", index)
        app.gui.setvar(_MODEL, "dune_x", default_row["x"])
        app.gui.setvar(_MODEL, "dune_y", default_row["y"])
        app.gui.setvar(_MODEL, "dune_wberm", default_row["wberm"])
        app.gui.setvar(_MODEL, "dune_dfelev", default_row["dfelev"])
        app.gui.setvar(_MODEL, "dune_dcelev", default_row["dcelev"])
        app.gui.setvar(_MODEL, "dune_cs", self._display_optional_float(default_row["cs"]))
        app.gui.setvar(_MODEL, "dune_cstill", self._display_optional_float(default_row["cstill"]))
        app.gui.setvar(_MODEL, "dune_xtill", self._display_optional_float(default_row["xtill"]))
        app.gui.setvar(_MODEL, "dune_perctill", self._display_optional_float(default_row["perctill"]))

    def _default_dune_row(self, x, y):
        variables = self.domain.input.variables
        return {
            "x": float(x),
            "y": float(y),
            "wberm": self._as_float(self._get_gui("wberm", getattr(variables, "wberm", 50.0)), 50.0),
            "dfelev": self._as_float(self._get_gui("dfelev", getattr(variables, "dfelev", 3.0)), 3.0),
            "dcelev": self._as_float(self._get_gui("dcelev", getattr(variables, "dcelev", 8.0)), 8.0),
            "cs": self._as_optional_float(self._get_gui("cs", getattr(variables, "cs", np.nan))),
            "cstill": self._as_optional_float(
                self._get_gui("cstill", getattr(variables, "cstill", np.nan))
            ),
            "xtill": self._as_optional_float(self._get_gui("xtill", getattr(variables, "xtill", np.nan))),
            "perctill": self._as_optional_float(
                self._get_gui("perctill", getattr(variables, "perctill", np.nan))
            ),
            "geometry": Point(float(x), float(y)),
        }

    def _dunes_from_gdf(self):
        if self.dunes_gdf is None or len(self.dunes_gdf.index) == 0:
            return np.empty((0, 0), dtype=float)
        work = self.dunes_gdf if self.dunes_gdf.crs is not None else self.dunes_gdf.set_crs(app.crs)
        if work.crs != self.domain.crs:
            work = work.to_crs(self.domain.crs)
        rows = []
        for _, row in work.iterrows():
            geom = row.geometry
            rows.append(
                [
                    float(geom.x),
                    float(geom.y),
                    self._as_float(row.get("wberm"), self.domain.input.variables.wberm),
                    self._as_float(row.get("dfelev"), self.domain.input.variables.dfelev),
                    self._as_float(row.get("dcelev"), self.domain.input.variables.dcelev),
                    self._as_optional_float(row.get("cs", np.nan)),
                    self._as_optional_float(row.get("cstill", np.nan)),
                    self._as_optional_float(row.get("xtill", np.nan)),
                    self._as_optional_float(row.get("perctill", np.nan)),
                ]
            )
        data = np.asarray(rows, dtype=float)
        while data.shape[1] > 5 and np.all(np.isnan(data[:, -1])):
            data = data[:, :-1]
        return data

    def _as_optional_float(self, value):
        if value is None:
            return np.nan
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return np.nan
        try:
            return float(value)
        except (TypeError, ValueError):
            return np.nan

    def _display_optional_float(self, value):
        if pd.isna(value):
            return ""
        return value
