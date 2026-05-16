import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def _install_import_stubs():
    gpd = types.ModuleType("geopandas")
    gpd.GeoDataFrame = object
    sys.modules.setdefault("geopandas", gpd)

    pyproj = types.ModuleType("pyproj")

    class CRS:
        @staticmethod
        def from_user_input(value):
            return value

    pyproj.CRS = CRS
    sys.modules.setdefault("pyproj", pyproj)

    shapely = types.ModuleType("shapely")
    geometry = types.ModuleType("shapely.geometry")

    class LineString:
        def __init__(self, coords=None):
            self.coords = coords or []
            self.is_empty = not self.coords

    class MultiLineString:
        def __init__(self, geoms=None):
            self.geoms = geoms or []
            self.is_empty = not self.geoms

    class Point:
        def __init__(self, x=0.0, y=0.0):
            self.x = x
            self.y = y
            self.is_empty = False

    def box(*args):
        return args

    geometry.LineString = LineString
    geometry.MultiLineString = MultiLineString
    geometry.Point = Point
    geometry.box = box
    shapely.geometry = geometry
    sys.modules.setdefault("shapely", shapely)
    sys.modules.setdefault("shapely.geometry", geometry)

    map_module = types.ModuleType("delftdashboard.operations.map")
    map_module.set_crs = lambda value: value
    sys.modules.setdefault("delftdashboard.operations.map", map_module)


_install_import_stubs()

sys.path.insert(0, r"D:\OSS\github_repos\delftdashboard\src")
sys.path.insert(0, r"D:\OSS\github_repos\cht_shorelines")

from delftdashboard.models.shorelines.shorelines import Model  # noqa: E402


def make_model():
    model = object.__new__(Model)
    model.runfile = "case.txt"
    model.nourishment_geometry_mode = "nor"
    model.polygon_nourishment_file = ""
    return model


def make_variables():
    return SimpleNamespace(
        ldbcoastline="coast.ldb",
        xmc="",
        ymc="",
        ldbstructures="structures.ldb",
        xhard=[1.0],
        yhard=[2.0],
        struct=1,
        ldbrevetments="revetments.ldb",
        xrevet=[3.0],
        yrevet=[4.0],
        revet=1,
        ldbdune="dunes.dun",
        dune=1,
        wberm=50.0,
        dfelev=3.0,
        dcelev=8.0,
        cs=0.0005,
        cstill=5.0e-06,
        xtill=[],
        perctill=80.0,
        norfile="nourishments.nor",
        ldbnourish="",
        nourstartfile="",
        nourendfile="",
        nourratefile="",
        nourish=1,
        reftime="2020-01-01",
        endofsimulation="2020-12-31",
        nourrate=3650.0,
        wvcfile="waves.wvc",
        waveclimfile="legacy.wvc",
    )


def make_domain(variables=None):
    variables = variables or make_variables()
    captured_dunes = {}
    return SimpleNamespace(
        crs="epsg:4326",
        input=SimpleNamespace(variables=variables, runfile="case.txt"),
        grid=SimpleNamespace(
            coastline="stale-coast",
            coastline_file="coast.ldb",
            extra_xy_files={},
            set_xy_file=lambda variable_name, coordinates, file_name: None,
        ),
        structures=SimpleNamespace(
            structures="stale-structures",
            structures_file="structures.ldb",
            revetments="stale-revetments",
            revetments_file="revetments.ldb",
        ),
        initial_conditions=SimpleNamespace(
            dunes="stale-dunes",
            dune_file="dunes.dun",
        ),
        dunes=SimpleNamespace(
            set_dunes=lambda data, file_name: captured_dunes.update(
                {"data": data, "file_name": file_name}
            )
        ),
        nourishments=SimpleNamespace(
            nourishments="stale-nourishments",
            nourishment_file="nourishments.nor",
            set_nourishments=lambda data, file_name: None,
        ),
        wave_boundary_conditions=SimpleNamespace(
            wave_timeseries={},
            spatial_wave_points=[],
            spatial_wave_file=None,
            wave_climate=None,
        ),
        _captured_dunes=captured_dunes,
    )


class ShorelinesModelTests(unittest.TestCase):
    def test_coerce_like_parses_numeric_sequences(self):
        model = make_model()

        self.assertEqual(model._coerce_like("30 40", []), [30, 40])
        self.assertEqual(model._coerce_like("[1 2; 3 4]", []), [[1, 2], [3, 4]])

    def test_set_model_variables_clears_legacy_waveclimfile_for_constant_input(self):
        model = make_model()
        model.domain = make_domain()
        model._get_gui = lambda name, default=None: {
            "runfile": "case.txt",
            "wave_input_type": "constant",
        }.get(name, default)

        model.set_model_variables()

        self.assertEqual(model.domain.input.variables.wvcfile, "")
        self.assertEqual(model.domain.input.variables.waveclimfile, "")

    def test_sync_geometry_to_domain_clears_stale_empty_feature_state(self):
        model = make_model()
        model.domain = make_domain()
        model._get_gui = lambda name, default=None: default
        model.coastline_gdf = None
        model.structures_gdf = None
        model.revetments_gdf = None
        model.dunes_gdf = None
        model.nourishments_gdf = None

        model._sync_geometry_to_domain()

        variables = model.domain.input.variables
        self.assertEqual(variables.ldbcoastline, "")
        self.assertEqual(variables.ldbstructures, "")
        self.assertEqual(variables.ldbrevetments, "")
        self.assertEqual(variables.ldbdune, "")
        self.assertEqual(variables.dune, 0)
        self.assertEqual(variables.norfile, "")
        self.assertEqual(variables.ldbnourish, "")
        self.assertEqual(variables.nourish, 0)

    def test_sync_dunes_to_domain_writes_dune_file(self):
        model = make_model()
        model.domain = make_domain()
        model._get_gui = lambda name, default=None: {
            "ldbdune": "custom_dunes.dun",
        }.get(name, default)
        model._dunes_from_gdf = lambda: np.array([[1.0, 2.0, 12.0, 3.5, 8.5]])

        file_name = model._sync_dunes_to_domain()

        self.assertEqual(file_name, "custom_dunes.dun")
        self.assertEqual(model.domain.input.variables.ldbdune, "custom_dunes.dun")
        self.assertEqual(model.domain.input.variables.dune, 1)
        np.testing.assert_allclose(
            model.domain._captured_dunes["data"],
            np.array([[1.0, 2.0, 12.0, 3.5, 8.5]]),
        )
        self.assertEqual(model.domain._captured_dunes["file_name"], "custom_dunes.dun")

    def test_sync_polygon_nourishments_preserves_polygon_mode_and_writes_metadata(self):
        model = make_model()
        model.nourishment_geometry_mode = "polygon"
        model.polygon_nourishment_file = "areas.ldb"
        model.nourishments_gdf = object()

        with tempfile.TemporaryDirectory() as tmpdir:
            variables = make_variables()
            variables.norfile = ""
            variables.ldbnourish = "areas.ldb"
            domain = make_domain(variables)

            def set_xy_file(variable_name, coordinates, file_name):
                domain.grid.extra_xy_files[variable_name] = (file_name, coordinates)

            domain.grid.set_xy_file = set_xy_file
            model.domain = domain
            model.path = tmpdir
            model._nourishments_from_gdf = lambda: [
                {
                    "tstart": 20200101,
                    "tend": 20200111,
                    "totalvolume": 100.0,
                }
            ]
            model._sections_from_gdf = lambda gdf: [
                np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
            ]

            file_name = model._sync_nourishments_to_domain()

            self.assertEqual(file_name, "areas.ldb")
            self.assertEqual(model.domain.input.variables.norfile, "")
            self.assertEqual(model.domain.input.variables.ldbnourish, "areas.ldb")
            self.assertEqual(model.domain.input.variables.nourish, 1)
            self.assertIn("ldbnourish", model.domain.grid.extra_xy_files)

            start_path = Path(tmpdir) / model.domain.input.variables.nourstartfile
            end_path = Path(tmpdir) / model.domain.input.variables.nourendfile
            rate_path = Path(tmpdir) / model.domain.input.variables.nourratefile

            self.assertTrue(start_path.exists())
            self.assertTrue(end_path.exists())
            self.assertTrue(rate_path.exists())
            self.assertEqual(start_path.read_text(encoding="utf-8").strip(), "2020-01-01")
            self.assertEqual(end_path.read_text(encoding="utf-8").strip(), "2020-01-11")
            self.assertEqual(rate_path.read_text(encoding="utf-8").strip(), "3650.000000")

    def test_infer_wave_input_type_uses_loaded_boundary_content(self):
        model = make_model()
        variables = make_variables()
        domain = make_domain(variables)
        domain.wave_boundary_conditions.wave_timeseries = {"waves.wvt": object()}
        variables.wvcfile = "waves.wvt"
        variables.waveclimfile = ""
        model.domain = domain

        self.assertEqual(model._infer_wave_input_type(variables), "timeseries")

        domain.wave_boundary_conditions.wave_timeseries = {}
        domain.wave_boundary_conditions.wave_climate = object()
        variables.wvcfile = "waves.wvc"

        self.assertEqual(model._infer_wave_input_type(variables), "climate")


if __name__ == "__main__":
    unittest.main()
