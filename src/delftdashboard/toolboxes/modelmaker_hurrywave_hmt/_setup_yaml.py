"""Hydromt-hurrywave build YAML I/O for the HurryWave HydroMT Model Maker.

Defines :class:`SetupYamlMixin`, mixed into the toolbox ``Toolbox`` so
``read_setup_yaml`` / ``write_setup_yaml`` stay accessible as bound
methods (the GUI YAMLs and external callers expect them there).

Emits the standard hydromt build config (``global`` + ``steps``).
Recognised steps: ``quadtree_grid.create``, ``quadtree_elevation.create``,
``quadtree_mask.create`` and ``wave_blocking.create``.
"""

from __future__ import annotations

from cht_utils.fileio.yaml import dict2yaml, yaml2dict
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.topography import to_hydromt_elevation_list


_TB = "modelmaker_hurrywave_hmt"


class SetupYamlMixin:
    """Mixin providing setup-YAML I/O methods on the HurryWave HMT Toolbox."""

    def write_setup_yaml(self) -> None:
        """Write the current setup as a hydromt-hurrywave build YAML.

        The output file follows the hydromt build-config schema (``global``
        + ``steps``) and can be passed straight to::

            hydromt build hurrywave <root> -i model_setup_hurrywave.yml
        """
        x0 = float(app.gui.getvar(_TB, "x0"))
        y0 = float(app.gui.getvar(_TB, "y0"))
        dx = float(app.gui.getvar(_TB, "dx"))
        dy = float(app.gui.getvar(_TB, "dy"))
        nmax = int(app.gui.getvar(_TB, "nmax"))
        mmax = int(app.gui.getvar(_TB, "mmax"))
        rotation = float(app.gui.getvar(_TB, "rotation"))
        epsg = app.crs.to_epsg() if app.crs is not None else None

        grid_args: dict = {
            "x0": x0,
            "y0": y0,
            "dx": dx,
            "dy": dy,
            "nmax": nmax,
            "mmax": mmax,
            "rotation": rotation,
        }
        if epsg is not None:
            grid_args["epsg"] = epsg
        if len(self.refinement_polygon) > 0:
            grid_args["refinement_polygons"] = app.gui.getvar(
                _TB, "refinement_polygon_file"
            )

        steps: list = [{"quadtree_grid.create": grid_args}]

        # Bathymetry / elevation. Build a fresh list per step so PyYAML
        # doesn't emit a shared-reference anchor (e.g. ``&id001``).
        if app.selected_bathymetry_datasets:
            steps.append(
                {
                    "quadtree_elevation.create": {
                        "elevation_list": to_hydromt_elevation_list(
                            app.selected_bathymetry_datasets
                        )
                    }
                }
            )

        # Mask (active + open boundary). HurryWave only has include /
        # exclude / open_boundary kinds.
        mask_args: dict = {
            "zmin": app.gui.getvar(_TB, "global_zmin"),
            "zmax": app.gui.getvar(_TB, "global_zmax"),
        }
        if len(self.include_polygon) > 0:
            mask_args["include_polygon"] = self.include_file_name
            mask_args["include_zmin"] = app.gui.getvar(_TB, "include_zmin")
            mask_args["include_zmax"] = app.gui.getvar(_TB, "include_zmax")
        if len(self.exclude_polygon) > 0:
            mask_args["exclude_polygon"] = self.exclude_file_name
            mask_args["exclude_zmin"] = app.gui.getvar(_TB, "exclude_zmin")
            mask_args["exclude_zmax"] = app.gui.getvar(_TB, "exclude_zmax")
        if len(self.boundary_polygon) > 0:
            mask_args["open_boundary_polygon"] = self.boundary_file_name
            mask_args["open_boundary_zmin"] = app.gui.getvar(_TB, "boundary_zmin")
            mask_args["open_boundary_zmax"] = app.gui.getvar(_TB, "boundary_zmax")
        steps.append({"quadtree_mask.create": mask_args})

        # Optional ``cut_inactive_cells`` step. Only emitted if the user
        # actually clicked "Cut Inactive Cells" in the current session;
        # a fresh build (re-generating the grid) resets the flag.
        if getattr(self, "_inactive_cells_cut", False):
            steps.append({"quadtree_grid.cut_inactive_cells": {}})

        # Optional wave-blocking step (own elevation_list copy — see above).
        if app.gui.getvar(_TB, "use_waveblocking") and app.selected_bathymetry_datasets:
            steps.append(
                {
                    "wave_blocking.create": {
                        "elevation_list": to_hydromt_elevation_list(
                            app.selected_bathymetry_datasets
                        ),
                        "nr_subgrid_pixels": app.gui.getvar(
                            _TB, "waveblocking_nr_pixels"
                        ),
                        "threshold_level": app.gui.getvar(
                            _TB, "waveblocking_threshold_level"
                        ),
                    }
                }
            )

        # Emit the catalog YAML(s) that back the selected bathymetry
        # datasets so the setup yaml is directly runnable with
        # ``hydromt build hurrywave <root> -i model_setup_hurrywave.yml``.
        data_libs = app.topography_data_catalog.data_libs_for(
            [d["name"] for d in app.selected_bathymetry_datasets]
        )
        dct = {"global": {"data_libs": data_libs}, "steps": steps}
        self.setup_dict = dct
        dict2yaml("model_setup_hurrywave.yml", dct)

    def read_setup_yaml(self, file_name: str) -> None:
        """Read a hydromt-hurrywave build YAML and populate GUI state and polygons.

        Expects the format produced by :py:meth:`write_setup_yaml`
        (``global`` + ``steps``). Recognises ``quadtree_grid.create``,
        ``quadtree_elevation.create``, ``quadtree_mask.create`` and
        ``wave_blocking.create``.
        """
        # Reset state.
        self.initialize()

        dct = yaml2dict(file_name)
        self.setup_dict = dct

        step_args: dict[str, dict] = {}
        for step in dct.get("steps", []):
            if not isinstance(step, dict) or not step:
                continue
            key, args = next(iter(step.items()))
            step_args[key] = args or {}

        # ------------------------------------------------------------------
        # Grid
        # ------------------------------------------------------------------
        grid = step_args.get("quadtree_grid.create")
        if grid is None:
            print("Warning: no quadtree_grid.create step found in setup yaml.")
            return

        x0 = float(grid["x0"])
        y0 = float(grid["y0"])
        dx = float(grid["dx"])
        dy = float(grid["dy"])
        nmax = int(grid["nmax"])
        mmax = int(grid["mmax"])
        rotation = float(grid.get("rotation", 0.0))

        app.gui.setvar(_TB, "x0", x0)
        app.gui.setvar(_TB, "y0", y0)
        app.gui.setvar(_TB, "dx", dx)
        app.gui.setvar(_TB, "dy", dy)
        app.gui.setvar(_TB, "nmax", nmax)
        app.gui.setvar(_TB, "mmax", mmax)
        app.gui.setvar(_TB, "rotation", rotation)

        # The HurrywaveModel's CRS is read-only and only set when the grid
        # is built — store the CRS at the app/map level instead. The grid
        # itself picks it up via app.crs.to_epsg() in generate_grid.
        if "epsg" in grid:
            crs_obj = CRS.from_epsg(int(grid["epsg"]))
        elif "crs" in grid:
            crs_obj = CRS(grid["crs"])
        else:
            crs_obj = app.crs
        map.set_crs(crs_obj)

        # Zoom to the model outline.
        x1 = x0 + dx * mmax
        y1 = y0 + dy * nmax
        app.map.fit_bounds(
            x0 - 0.1 * (x1 - x0), y0 - 0.1 * (y1 - y0),
            x1 + 0.1 * (x1 - x0), y1 + 0.1 * (y1 - y0),
            crs=crs_obj,
        )

        # Optional refinement polygons.
        ref_file = grid.get("refinement_polygons")
        if ref_file:
            app.gui.setvar(_TB, "refinement_polygon_file", ref_file)
            self.read_refinement_polygon(ref_file, False)
            self.plot_refinement_polygon()

        # ------------------------------------------------------------------
        # Bathymetry / elevation. Either elevation step or wave_blocking
        # step may carry an elevation_list; we union them, deduplicating
        # by dataset name (first occurrence wins for zmin/zmax).
        # ------------------------------------------------------------------
        from delftdashboard.operations import bathy_topo_selector

        elevation_entries = []
        for step_key in ("quadtree_elevation.create", "wave_blocking.create"):
            step = step_args.get(step_key, {}) or {}
            elevation_entries.extend(step.get("elevation_list", []) or [])

        seen: set[str] = set()
        app.selected_bathymetry_datasets.clear()
        for entry in elevation_entries:
            name = entry.get("name") or entry.get("elevation") or entry.get("da")
            if name is None or name in seen:
                continue
            seen.add(name)
            app.selected_bathymetry_datasets.append(
                {
                    "name": name,
                    "zmin": entry.get("zmin", -99999.0),
                    "zmax": entry.get("zmax", 99999.0),
                }
            )
        self.selected_bathymetry_datasets = app.selected_bathymetry_datasets
        bathy_topo_selector.update()

        # ------------------------------------------------------------------
        # Mask (active + boundary)
        # ------------------------------------------------------------------
        mask = step_args.get("quadtree_mask.create", {})
        if "zmin" in mask:
            app.gui.setvar(_TB, "global_zmin", mask["zmin"])
        if "zmax" in mask:
            app.gui.setvar(_TB, "global_zmax", mask["zmax"])

        # Map hydromt mask kwargs → DDB GUI vars + polygon readers.
        for kind, ddb_prefix, reader_name, plotter_name in [
            ("include_polygon",       "include",  "read_include_polygon",  "plot_include_polygon"),
            ("exclude_polygon",       "exclude",  "read_exclude_polygon",  "plot_exclude_polygon"),
            ("open_boundary_polygon", "boundary", "read_boundary_polygon", "plot_boundary_polygon"),
        ]:
            poly_arg = mask.get(kind)
            if isinstance(poly_arg, str):
                key_prefix = kind.removesuffix("_polygon")  # "open_boundary" / "include" / "exclude"
                zmin_arg = mask.get(f"{key_prefix}_zmin")
                zmax_arg = mask.get(f"{key_prefix}_zmax")
                if zmin_arg is not None:
                    app.gui.setvar(_TB, f"{ddb_prefix}_zmin", zmin_arg)
                if zmax_arg is not None:
                    app.gui.setvar(_TB, f"{ddb_prefix}_zmax", zmax_arg)
                # Remember the file name so re-saving uses the same path.
                setattr(self, f"{ddb_prefix}_file_name", poly_arg)
                getattr(self, reader_name)(poly_arg, False)
                getattr(self, plotter_name)()

        # Remember whether the setup YAML requested a cut_inactive_cells
        # step; ``build_model`` replays it only when the flag is set.
        self._inactive_cells_cut = "quadtree_grid.cut_inactive_cells" in step_args

        # ------------------------------------------------------------------
        # Wave blocking (toggle + parameters if present)
        # ------------------------------------------------------------------
        wb = step_args.get("wave_blocking.create")
        if wb is not None:
            app.gui.setvar(_TB, "use_waveblocking", True)
            if "nr_subgrid_pixels" in wb:
                app.gui.setvar(_TB, "waveblocking_nr_pixels", wb["nr_subgrid_pixels"])
            if "threshold_level" in wb:
                app.gui.setvar(_TB, "waveblocking_threshold_level", wb["threshold_level"])
        else:
            app.gui.setvar(_TB, "use_waveblocking", False)

        # ------------------------------------------------------------------
        # Grid outline rectangle on the map
        # ------------------------------------------------------------------
        layer = app.map.layer[_TB].layer["grid_outline"]
        layer.add_rectangle(x0, y0, dx * mmax, dy * nmax, rotation)
