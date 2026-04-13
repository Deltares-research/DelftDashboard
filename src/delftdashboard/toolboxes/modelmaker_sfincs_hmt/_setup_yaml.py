"""Hydromt-sfincs build YAML I/O for the SFINCS HydroMT Model Maker.

Defines :class:`SetupYamlMixin`, mixed into the toolbox ``Toolbox`` so
``read_setup_yaml`` / ``write_setup_yaml`` stay accessible as bound
methods (the GUI YAMLs and external callers expect them there).

The output schema is the standard hydromt build config (``global`` +
``steps``); each step is a single ``<component>.<method>`` mapping that
maps to one of the registered SFINCS components: ``quadtree_grid``,
``quadtree_elevation``, ``quadtree_mask``, ``quadtree_subgrid``, and
``quadtree_snapwave_mask``.
"""

from __future__ import annotations

from cht_utils.fileio.yaml import dict2yaml, yaml2dict
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.topography import to_hydromt_elevation_list


_TB = "modelmaker_sfincs_hmt"
_MODEL = "sfincs_hmt"


class SetupYamlMixin:
    """Mixin providing setup-YAML I/O methods on the SFINCS HMT Toolbox."""

    def read_setup_yaml(self, file_name: str) -> None:
        """Read a hydromt-sfincs build YAML and populate GUI state and polygons.

        Expects the format produced by :py:meth:`write_setup_yaml`
        (``global`` + ``steps``). Each step under ``steps`` is a single
        ``<component>.<method>`` mapping; the component names recognised
        here are ``quadtree_grid``, ``quadtree_elevation``,
        ``quadtree_mask``, ``quadtree_subgrid`` and
        ``quadtree_snapwave_mask``.
        """
        group = _TB

        # Reset map layers and toolbox state.
        self.clear_layers()
        self.initialize()

        dct = yaml2dict(file_name)
        self.setup_dict = dct

        # Index the steps by component name for easy lookup. A YAML build
        # config may legally repeat steps; here we keep the LAST occurrence
        # (typical workflows only have one of each for a fresh build).
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

        app.gui.setvar(group, "x0", x0)
        app.gui.setvar(group, "y0", y0)
        app.gui.setvar(group, "dx", dx)
        app.gui.setvar(group, "dy", dy)
        app.gui.setvar(group, "nmax", nmax)
        app.gui.setvar(group, "mmax", mmax)
        app.gui.setvar(group, "rotation", rotation)

        # The SfincsModel's CRS is read-only and only set when the grid is
        # built — store the CRS at the app/map level instead. The grid
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
        bounds = [x0 - 0.1 * (x1 - x0), y0 - 0.1 * (y1 - y0),
                  x1 + 0.1 * (x1 - x0), y1 + 0.1 * (y1 - y0)]
        app.map.fit_bounds(
            bounds[0], bounds[1], bounds[2], bounds[3], crs=crs_obj,
        )

        # Optional grid-refinement polygons.
        ref_file = grid.get("refinement_polygons")
        if ref_file:
            app.gui.setvar(group, "refinement_polygon_file", ref_file)
            self.read_refinement_polygon(ref_file, False)
            self.plot_refinement_polygon()

        # ------------------------------------------------------------------
        # Bathymetry / elevation. Either step may carry an elevation_list;
        # we union them, deduplicating by dataset name (first occurrence
        # wins for zmin/zmax).
        # ------------------------------------------------------------------
        elevation_entries = []
        for step_key in ("quadtree_elevation.create", "quadtree_subgrid.create"):
            step = step_args.get(step_key, {}) or {}
            elevation_entries.extend(step.get("elevation_list", []) or [])

        from delftdashboard.operations import bathy_topo_selector

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
        # Mirror onto the toolbox-local list and refresh the GUI list,
        # which is bound to the shared ``bathy_topo_selector`` group.
        self.selected_bathymetry_datasets = app.selected_bathymetry_datasets
        bathy_topo_selector.update()

        # ------------------------------------------------------------------
        # Mask (active + boundaries)
        # ------------------------------------------------------------------
        self._apply_mask_step(
            step_args.get("quadtree_mask.create", {}),
            snapwave=False,
        )

        # ------------------------------------------------------------------
        # Subgrid (optional)
        # ------------------------------------------------------------------
        sg_args = step_args.get("quadtree_subgrid.create")
        if sg_args is not None:
            app.gui.setvar(group, "use_subgrid", True)
            for yaml_key, gui_key in [
                ("manning_land", "manning_land"),
                ("manning_water", "manning_water"),
                ("manning_level", "manning_level"),
                ("nr_levels", "subgrid_nr_levels"),
                ("nr_subgrid_pixels", "subgrid_nr_pixels"),
                ("max_gradient", "subgrid_max_dzdv"),
                ("zmin", "subgrid_zmin"),
            ]:
                if yaml_key in sg_args:
                    app.gui.setvar(group, gui_key, sg_args[yaml_key])
        else:
            app.gui.setvar(group, "use_subgrid", False)

        # ------------------------------------------------------------------
        # SnapWave mask (optional)
        # ------------------------------------------------------------------
        sw_args = step_args.get("quadtree_snapwave_mask.create")
        if sw_args is not None:
            app.gui.setvar(group, "use_snapwave", True)
            self._apply_mask_step(sw_args, snapwave=True)
        else:
            app.gui.setvar(group, "use_snapwave", False)

        # ------------------------------------------------------------------
        # Grid outline rectangle on the map
        # ------------------------------------------------------------------
        layer = app.map.layer[_TB].layer["grid_outline"]
        layer.add_rectangle(x0, y0, dx * mmax, dy * nmax, rotation)

    def _apply_mask_step(self, args: dict, snapwave: bool) -> None:
        """Populate mask GUI vars and polygons from a hydromt mask step.

        Used by :py:meth:`read_setup_yaml` for both the SFINCS mask
        (``snapwave=False``) and the SnapWave mask (``snapwave=True``).
        """
        group = _TB
        suffix = "_snapwave" if snapwave else ""

        # Global zmin/zmax
        zmin = args.get("zmin")
        zmax = args.get("zmax")
        if not snapwave:
            app.gui.setvar(group, "use_mask_global", zmin is not None or zmax is not None)
        if zmin is not None:
            app.gui.setvar(group, f"global_zmin{suffix}", zmin)
        if zmax is not None:
            app.gui.setvar(group, f"global_zmax{suffix}", zmax)

        # Polygons. Each block is (kind, reader-method, plotter-method).
        # SnapWave doesn't support outflow / downstream boundaries.
        kinds = [
            ("include",            "read_include_polygon",            "plot_include_polygon"),
            ("exclude",            "read_exclude_polygon",            "plot_exclude_polygon"),
            ("open_boundary",      "read_open_boundary_polygon",      "plot_open_boundary_polygon"),
            ("neumann_boundary",   "read_neumann_boundary_polygon",   "plot_neumann_boundary_polygon"),
        ]
        if not snapwave:
            kinds += [
                ("outflow_boundary",    "read_outflow_boundary_polygon",    "plot_outflow_boundary_polygon"),
                ("downstream_boundary", "read_downstream_boundary_polygon", "plot_downstream_boundary_polygon"),
            ]

        for kind, reader_name, plotter_name in kinds:
            poly_arg = args.get(f"{kind}_polygon")
            zmin_arg = args.get(f"{kind}_zmin")
            zmax_arg = args.get(f"{kind}_zmax")
            if zmin_arg is not None:
                app.gui.setvar(group, f"{kind}_zmin{suffix}", zmin_arg)
            if zmax_arg is not None:
                app.gui.setvar(group, f"{kind}_zmax{suffix}", zmax_arg)
            if isinstance(poly_arg, str):
                app.gui.setvar(group, f"{kind}_polygon_file{suffix}", poly_arg)
                reader = getattr(self, reader_name + suffix)
                plotter = getattr(self, plotter_name + suffix)
                reader(poly_arg, False)
                plotter()

    def write_setup_yaml(self) -> None:
        """Write the current model setup as a hydromt-sfincs build YAML.

        The output file follows the hydromt build-config schema (``global``
        + ``steps``) and can be passed straight to::

            hydromt build sfincs <root> -i model_setup_sfincs.yml

        All polygons currently held in the toolbox are also serialised as
        sidecar GeoJSON files referenced from the YAML.
        """
        group = _TB

        # ------------------------------------------------------------------
        # Coordinates / grid build step
        # ------------------------------------------------------------------
        x0 = float(app.gui.getvar(group, "x0"))
        y0 = float(app.gui.getvar(group, "y0"))
        dx = float(app.gui.getvar(group, "dx"))
        dy = float(app.gui.getvar(group, "dy"))
        nmax = int(app.gui.getvar(group, "nmax"))
        mmax = int(app.gui.getvar(group, "mmax"))
        rotation = float(app.gui.getvar(group, "rotation"))
        crs = app.model[_MODEL].domain.crs
        epsg = crs.to_epsg() if crs is not None else None

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
        if len(app.toolbox[_TB].refinement_polygon) > 0:
            grid_args["refinement_polygons"] = app.gui.getvar(
                _TB, "refinement_polygon_file"
            )

        steps: list = [{"quadtree_grid.create": grid_args}]

        # ------------------------------------------------------------------
        # Bathymetry / elevation step. Build a fresh list per step so
        # PyYAML doesn't emit a shared-reference anchor (e.g. ``&id001``)
        # when the same elevation_list is reused by quadtree_subgrid.create
        # later on.
        # ------------------------------------------------------------------
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

        # ------------------------------------------------------------------
        # Mask step (active cells + boundary types)
        # ------------------------------------------------------------------
        mask_args: dict = {}
        if app.gui.getvar(group, "use_mask_global"):
            mask_args["zmin"] = app.gui.getvar(group, "global_zmin")
            mask_args["zmax"] = app.gui.getvar(group, "global_zmax")
        if len(app.toolbox[_TB].include_polygon) > 0:
            mask_args["include_polygon"] = app.gui.getvar(_TB, "include_polygon_file")
            mask_args["include_zmin"] = app.gui.getvar(_TB, "include_zmin")
            mask_args["include_zmax"] = app.gui.getvar(_TB, "include_zmax")
        if len(app.toolbox[_TB].exclude_polygon) > 0:
            mask_args["exclude_polygon"] = app.gui.getvar(_TB, "exclude_polygon_file")
            mask_args["exclude_zmin"] = app.gui.getvar(_TB, "exclude_zmin")
            mask_args["exclude_zmax"] = app.gui.getvar(_TB, "exclude_zmax")
        if len(app.toolbox[_TB].open_boundary_polygon) > 0:
            mask_args["open_boundary_polygon"] = app.gui.getvar(_TB, "open_boundary_polygon_file")
            mask_args["open_boundary_zmin"] = app.gui.getvar(_TB, "open_boundary_zmin")
            mask_args["open_boundary_zmax"] = app.gui.getvar(_TB, "open_boundary_zmax")
        if len(app.toolbox[_TB].outflow_boundary_polygon) > 0:
            mask_args["outflow_boundary_polygon"] = app.gui.getvar(_TB, "outflow_boundary_polygon_file")
            mask_args["outflow_boundary_zmin"] = app.gui.getvar(_TB, "outflow_boundary_zmin")
            mask_args["outflow_boundary_zmax"] = app.gui.getvar(_TB, "outflow_boundary_zmax")
        if len(app.toolbox[_TB].neumann_boundary_polygon) > 0:
            mask_args["neumann_boundary_polygon"] = app.gui.getvar(_TB, "neumann_boundary_polygon_file")
            mask_args["neumann_boundary_zmin"] = app.gui.getvar(_TB, "neumann_boundary_zmin")
            mask_args["neumann_boundary_zmax"] = app.gui.getvar(_TB, "neumann_boundary_zmax")
        if len(app.toolbox[_TB].downstream_boundary_polygon) > 0:
            mask_args["downstream_boundary_polygon"] = app.gui.getvar(_TB, "downstream_boundary_polygon_file")
            mask_args["downstream_boundary_zmin"] = app.gui.getvar(_TB, "downstream_boundary_zmin")
            mask_args["downstream_boundary_zmax"] = app.gui.getvar(_TB, "downstream_boundary_zmax")
        if mask_args:
            steps.append({"quadtree_mask.create": mask_args})

        # ------------------------------------------------------------------
        # Optional subgrid step
        # ------------------------------------------------------------------
        if app.gui.getvar(group, "use_subgrid"):
            sg_args: dict = {
                "elevation_list": to_hydromt_elevation_list(
                    app.selected_bathymetry_datasets
                ),
                "manning_land": app.gui.getvar(group, "manning_land"),
                "manning_water": app.gui.getvar(group, "manning_water"),
                "manning_level": app.gui.getvar(group, "manning_level"),
                "nr_levels": app.gui.getvar(group, "subgrid_nr_levels"),
                "nr_subgrid_pixels": app.gui.getvar(group, "subgrid_nr_pixels"),
                "max_gradient": app.gui.getvar(group, "subgrid_max_dzdv"),
                "zmin": app.gui.getvar(group, "subgrid_zmin"),
            }
            steps.append({"quadtree_subgrid.create": sg_args})

        # ------------------------------------------------------------------
        # Optional SnapWave mask step
        # ------------------------------------------------------------------
        if app.gui.getvar(group, "use_snapwave"):
            sw_args: dict = {
                "zmin": app.gui.getvar(group, "global_zmin_snapwave"),
                "zmax": app.gui.getvar(group, "global_zmax_snapwave"),
            }
            if len(app.toolbox[_TB].include_polygon_snapwave) > 0:
                sw_args["include_polygon"] = app.gui.getvar(_TB, "include_polygon_file_snapwave")
                sw_args["include_zmin"] = app.gui.getvar(_TB, "include_zmin_snapwave")
                sw_args["include_zmax"] = app.gui.getvar(_TB, "include_zmax_snapwave")
            if len(app.toolbox[_TB].exclude_polygon_snapwave) > 0:
                sw_args["exclude_polygon"] = app.gui.getvar(_TB, "exclude_polygon_file_snapwave")
                sw_args["exclude_zmin"] = app.gui.getvar(_TB, "exclude_zmin_snapwave")
                sw_args["exclude_zmax"] = app.gui.getvar(_TB, "exclude_zmax_snapwave")
            if len(app.toolbox[_TB].open_boundary_polygon_snapwave) > 0:
                sw_args["open_boundary_polygon"] = app.gui.getvar(_TB, "open_boundary_polygon_file_snapwave")
                sw_args["open_boundary_zmin"] = app.gui.getvar(_TB, "open_boundary_zmin_snapwave")
                sw_args["open_boundary_zmax"] = app.gui.getvar(_TB, "open_boundary_zmax_snapwave")
            if len(app.toolbox[_TB].neumann_boundary_polygon_snapwave) > 0:
                sw_args["neumann_boundary_polygon"] = app.gui.getvar(_TB, "neumann_boundary_polygon_file_snapwave")
                sw_args["neumann_boundary_zmin"] = app.gui.getvar(_TB, "neumann_boundary_zmin_snapwave")
                sw_args["neumann_boundary_zmax"] = app.gui.getvar(_TB, "neumann_boundary_zmax_snapwave")
            steps.append({"quadtree_snapwave_mask.create": sw_args})

        # ------------------------------------------------------------------
        # Assemble the hydromt build YAML
        # ------------------------------------------------------------------
        dct = {"global": {"data_libs": []}, "steps": steps}
        self.setup_dict = dct
        dict2yaml("model_setup_sfincs.yml", dct)

        # Write out polygons (sidecar GeoJSON files referenced from the YAML)
        app.toolbox[_TB].write_include_polygon()
        app.toolbox[_TB].write_exclude_polygon()
        app.toolbox[_TB].write_open_boundary_polygon()
        app.toolbox[_TB].write_downstream_boundary_polygon()
        app.toolbox[_TB].write_neumann_boundary_polygon()
        app.toolbox[_TB].write_outflow_boundary_polygon()
        app.toolbox[_TB].write_refinement_polygon()
        app.toolbox[_TB].write_include_polygon_snapwave()
        app.toolbox[_TB].write_exclude_polygon_snapwave()
        app.toolbox[_TB].write_open_boundary_polygon_snapwave()
        app.toolbox[_TB].write_neumann_boundary_polygon_snapwave()
