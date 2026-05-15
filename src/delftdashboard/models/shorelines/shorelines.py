import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, MultiLineString, box

import delftdashboard.operations.model
from delftdashboard.app import app
from delftdashboard.models.shorelines.domain import (
    coastline_created,
    coastline_modified,
    coastline_selected,
)
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

        self.coastline_gdf = self._empty_gdf()
        self.structures_gdf = self._empty_gdf()
        self.revetments_gdf = self._empty_gdf()
        self.nourishments_gdf = self._empty_gdf(
            {
                "tstart": pd.Series(dtype="float64"),
                "tend": pd.Series(dtype="float64"),
                "totalvolume": pd.Series(dtype="float64"),
            }
        )
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

    def set_layer_mode(self, mode):
        if _MODEL not in app.map.layer:
            return
        for name in ["coastline", "structures", "revetments", "nourishments"]:
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

        path = Path(filename)
        self.path = str(path.parent)
        self.runfile = path.name
        os.chdir(self.path)

        self.domain = self._new_domain(self.path, self.runfile)
        self.domain.input.read()
        self._load_attribute_files()
        self.set_gui_variables()
        self.plot()
        self.zoom_to_model()
        app.gui.window.update()

    def save(self):
        self.set_model_variables()
        self._sync_domain_path()
        self._sync_geometry_to_domain()
        self.domain.write()

    def plot(self):
        if _MODEL not in app.map.layer:
            return
        for name in ["coastline", "structures", "revetments", "nourishments"]:
            app.map.layer[_MODEL].layer[name].set_data(getattr(self, f"{name}_gdf"))
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
        app.gui.setvar(_MODEL, "active_nourishments", 0)
        app.gui.setvar(_MODEL, "nourishment_tstart", 20200101)
        app.gui.setvar(_MODEL, "nourishment_tend", 20400101)
        app.gui.setvar(_MODEL, "nourishment_totalvolume", 100000.0)

        variables = self.domain.input.variables
        wave_input_type = "constant" if not variables.wvcfile else "climate"
        app.gui.setvar(_MODEL, "wave_input_type", wave_input_type)
        for name, value in vars(variables).items():
            app.gui.setvar(_MODEL, name, self._value_for_gui(value))

        self._set_list_vars()

    def set_model_variables(self):
        self.runfile = self._get_gui("runfile", self.runfile)
        self.domain.input.runfile = self.runfile

        variables = self.domain.input.variables
        for name, current in vars(variables).items():
            setattr(variables, name, self._coerce_like(self._get_gui(name, current), current))

        wave_input_type = self._get_gui("wave_input_type", "constant")
        if wave_input_type == "constant":
            variables.wvcfile = ""
        else:
            variables.wvcfile = self._get_gui("wvcfile", variables.wvcfile)

    def select_layer(self, layer_name):
        app.map.layer[_MODEL].layer[layer_name].activate()
        app.gui.window.update()

    def draw_feature(self, layer_name):
        app.map.layer[_MODEL].layer[layer_name].draw()

    def delete_feature(self, layer_name):
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
            filter="XY files (*.ldb *.xy *.nor *.txt);;All files (*)",
        )
        if not filename:
            return
        if isinstance(filename, (list, tuple)):
            filename = filename[0]
        if not filename:
            return
        if layer_name == "nourishments" and self._looks_like_nourishment_file(filename):
            gdf = self._load_optional_nourishments(filename)
        else:
            gdf = self._gdf_from_xy_file(filename)
        setattr(self, f"{layer_name}_gdf", gdf)
        self._set_list_vars()
        self.plot()

    def _sync_domain_path(self):
        self.domain.path = self.path
        self.domain.input.root = Path(self.path)

    def _sync_geometry_to_domain(self):
        variables = self.domain.input.variables

        coastline_file = self._get_gui("ldbcoastline", variables.ldbcoastline) or "coastline.ldb"
        coastline = self._sections_from_gdf(self.coastline_gdf)
        if coastline:
            self.domain.grid.set_coastline(coastline, file_name=coastline_file)

        structures = self._sections_from_gdf(self.structures_gdf)
        if structures:
            self.domain.structures.set_structures(
                structures,
                file_name=self._get_gui("ldbstructures", variables.ldbstructures) or "structures.ldb",
            )

        revetments = self._sections_from_gdf(self.revetments_gdf)
        if revetments:
            self.domain.structures.set_revetments(
                revetments,
                file_name=self._get_gui("ldbrevetments", variables.ldbrevetments) or "revetments.ldb",
            )

        nourishments = self._nourishments_from_gdf()
        if nourishments:
            self.domain.nourishments.set_nourishments(
                nourishments,
                file_name=self._get_gui("norfile", variables.norfile) or "nourishments.nor",
            )

    def _load_attribute_files(self):
        variables = self.domain.input.variables
        self.coastline_gdf = self._load_optional_xy(variables.ldbcoastline)
        self.structures_gdf = self._load_optional_xy(variables.ldbstructures)
        self.revetments_gdf = self._load_optional_xy(variables.ldbrevetments)
        self.nourishments_gdf = self._load_optional_nourishments(variables.norfile)
        self._set_list_vars()

    def _load_optional_xy(self, file_name):
        if not file_name:
            return self._empty_gdf()
        path = Path(self.path) / file_name
        if not path.exists():
            return self._empty_gdf()
        return self._gdf_from_xy_file(path)

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
        app.gui.window.update()

    def _set_list_vars(self):
        for name in ["coastline", "structures", "revetments", "nourishments"]:
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
        return value

    def _as_float(self, value, default):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _as_date_int(self, value, default):
        text = str(value).strip()
        if text.endswith(".0"):
            text = text[:-2]
        if text.isdigit() and len(text) == 8:
            return int(text)
        return default

    def _as_bool(self, value):
        if isinstance(value, str):
            return value.strip().lower() in ["1", "true", "yes", "on"]
        return bool(value)
