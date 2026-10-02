"""Spatial output tab of the Output Visualization toolbox.

Visualizes SFINCS map output (``sfincs_map.nc``) on the map as a datashader
trimesh overlay, mirroring how the model bathymetry is rendered via
hydromt_sfincs ``workflows.map_overlay`` (a per-cell coloured overlay that
re-renders for the current view on every pan/zoom, with a colorbar legend).

Supports both quadtree (UGRID ``mesh2d_*``) and regular (``n``/``m`` with
``corner_x`` / ``corner_y``) SFINCS map files.
"""

from __future__ import annotations

import os
from typing import Any, List, Optional

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import CRS, Transformer

from delftdashboard.app import app
from delftdashboard.operations import map

_G = "observation_timeseries"

# (netCDF variable, GUI label, time dimension or None). First is the default.
_MAP_VARIABLES: List[tuple[str, str, Optional[str]]] = [
    ("zsmax", "Max water level", "timemax"),
    ("hmax", "Max water depth", "timemax"),
    ("zs", "Water level", "time"),
    ("h", "Water depth", "time"),
    ("zb", "Bed level", None),
]

_CMAPS = ["viridis", "Blues", "turbo", "jet", "RdBu_r", "gist_earth"]


class QuadtreeMapOverlay:
    """Datashader trimesh overlay for a SFINCS quadtree map result.

    The mesh geometry (per-face quads split into two triangles, reprojected to
    EPSG:3857) is built once; only the per-vertex ``z`` column changes when the
    selected variable/time changes. ``map_overlay`` is called by the guitares
    raster-image layer for the current view extent.
    """

    def __init__(
        self, x3857: np.ndarray, y3857: np.ndarray, simplices: pd.DataFrame
    ) -> None:
        self._verts = pd.DataFrame(
            {"x": x3857, "y": y3857, "z": np.full(x3857.size, np.nan)}
        )
        self._simplices = simplices

    def set_values(self, z_face: np.ndarray) -> None:
        """Set the per-face values (4 vertices per face)."""
        self._verts["z"] = np.repeat(np.asarray(z_face, dtype=float), 4)

    def map_overlay(
        self,
        file_name,
        xlim=None,
        ylim=None,
        cmap: str = "viridis",
        cmin: Optional[float] = None,
        cmax: Optional[float] = None,
        width: int = 800,
        **kwargs: Any,
    ) -> bool:
        """Render the overlay PNG for the current view (delegates to hydromt_sfincs)."""
        from hydromt_sfincs.workflows.map_overlay import make_elevation_overlay

        return make_elevation_overlay(
            self._verts,
            self._simplices,
            file_name,
            xlim=xlim,
            ylim=ylim,
            cmap=cmap,
            cmin=cmin,
            cmax=cmax,
            width=width,
        )


# ----------------------------------------------------------------------
# Setup (called from the toolbox)
# ----------------------------------------------------------------------


def initialize(tb) -> None:
    """Initialise spatial state and GUI variables on the toolbox instance."""
    tb.spatial_ds = None
    tb.spatial_overlay = None
    tb.spatial_crs = None
    tb.spatial_bounds = None  # (lon0, lat0, lon1, lat1)

    app.gui.setvar(_G, "spatial_variable_values", [v[0] for v in _MAP_VARIABLES])
    app.gui.setvar(_G, "spatial_variable_strings", [v[1] for v in _MAP_VARIABLES])
    app.gui.setvar(_G, "spatial_variable", _MAP_VARIABLES[0][0])
    app.gui.setvar(_G, "spatial_time_strings", [""])
    app.gui.setvar(_G, "spatial_time_index", 0)
    app.gui.setvar(_G, "spatial_cmap_values", _CMAPS)
    app.gui.setvar(_G, "spatial_cmap_strings", _CMAPS)
    app.gui.setvar(_G, "spatial_cmap", _CMAPS[0])
    app.gui.setvar(_G, "spatial_cmin", 0.0)
    app.gui.setvar(_G, "spatial_cmax", 2.0)
    app.gui.setvar(_G, "spatial_opacity", 0.7)
    app.gui.setvar(_G, "spatial_basemap_values", ["none", "sat", "osm", "light"])
    app.gui.setvar(
        _G, "spatial_basemap_strings", ["None", "Satellite", "OpenStreetMap", "Light"]
    )
    app.gui.setvar(_G, "spatial_basemap", "none")
    app.gui.setvar(_G, "spatial_map_file_string", "File : ")


def add_layer(layer) -> None:
    """Add the spatial raster-image overlay sublayer to the toolbox layer."""
    layer.add_layer(
        "spatial",
        type="raster_image",
        map_overlay_options=spatial_overlay_options,
        legend_position="bottom-right",
        opacity=0.7,
    )


def spatial_overlay_options() -> dict:
    """Colormap/limits passed to the overlay on each render (drives the legend)."""
    try:
        return {
            "cmap": app.gui.getvar(_G, "spatial_cmap"),
            "cmin": float(app.gui.getvar(_G, "spatial_cmin")),
            "cmax": float(app.gui.getvar(_G, "spatial_cmax")),
        }
    except Exception:
        return {"cmap": "viridis", "cmin": 0.0, "cmax": 2.0}


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _time_dim(variable: str) -> Optional[str]:
    for var, _label, tdim in _MAP_VARIABLES:
        if var == variable:
            return tdim
    return None


def _file_crs(ds: xr.Dataset) -> Optional[CRS]:
    """Resolve the CRS from the ``crs`` variable, falling back to ``inp``."""
    for name in ("crs", "inp"):
        if name in ds:
            attrs = ds[name].attrs
            code = attrs.get("epsg_code") or attrs.get("epsg")
            if code is None or str(code) in ("-", ""):
                continue
            for candidate in (code, str(code)):
                try:
                    return CRS.from_user_input(candidate)
                except Exception:
                    continue
    return None


def _is_quadtree(ds: xr.Dataset) -> bool:
    """Return True for a UGRID quadtree map file, False for a regular grid."""
    return "mesh2d_face_nodes" in ds.variables


def _simplices_for(ncell: int) -> pd.DataFrame:
    """Two triangles per cell over per-cell 4-vertex blocks."""
    base = np.arange(ncell) * 4
    tris = np.vstack(
        [
            np.column_stack([base, base + 1, base + 2]),
            np.column_stack([base, base + 2, base + 3]),
        ]
    )
    return pd.DataFrame({"v0": tris[:, 0], "v1": tris[:, 1], "v2": tris[:, 2]})


def _build_geometry_regular(ds: xr.Dataset, crs: CRS):
    """Build (x3857, y3857, simplices) for a regular (n, m) SFINCS grid.

    Cell corners come from ``corner_x`` / ``corner_y`` (shape (n+1, m+1)); each
    cell becomes 4 vertices (2 triangles). Vertex order matches the C-order
    flattening of the (n, m) cell values.
    """
    cx = np.asarray(ds["corner_x"].values, dtype=float)
    cy = np.asarray(ds["corner_y"].values, dtype=float)
    vx = np.stack(
        [cx[:-1, :-1], cx[1:, :-1], cx[1:, 1:], cx[:-1, 1:]], axis=-1
    ).reshape(-1)
    vy = np.stack(
        [cy[:-1, :-1], cy[1:, :-1], cy[1:, 1:], cy[:-1, 1:]], axis=-1
    ).reshape(-1)
    transformer = Transformer.from_crs(crs, 3857, always_xy=True)
    x3857, y3857 = transformer.transform(vx, vy)
    ncell = (cx.shape[0] - 1) * (cx.shape[1] - 1)
    return x3857, y3857, _simplices_for(ncell)


def _build_geometry(ds: xr.Dataset, crs: CRS):
    """Build (x3857, y3857, simplices) for a quadtree mesh."""
    nx = np.asarray(ds["mesh2d_node_x"].values, dtype=float)
    ny = np.asarray(ds["mesh2d_node_y"].values, dtype=float)
    fn = ds["mesh2d_face_nodes"]
    start = int(fn.attrs.get("start_index", 0))
    idx = np.asarray(fn.values, dtype=np.int64) - start
    idx = np.clip(idx, 0, nx.size - 1)  # guard against fill values

    vx = nx[idx].ravel()
    vy = ny[idx].ravel()
    transformer = Transformer.from_crs(crs, 3857, always_xy=True)
    x3857, y3857 = transformer.transform(vx, vy)

    nface = idx.shape[0]
    base = np.arange(nface) * 4
    tris = np.vstack(
        [
            np.column_stack([base, base + 1, base + 2]),
            np.column_stack([base, base + 2, base + 3]),
        ]
    )
    simplices = pd.DataFrame({"v0": tris[:, 0], "v1": tris[:, 1], "v2": tris[:, 2]})
    return x3857, y3857, simplices


def _native_vertices(ds: xr.Dataset, quadtree: bool):
    """Return per-cell 4-vertex coordinates in the file's native CRS.

    Returns ``(vx, vy, ncell)`` where ``vx``/``vy`` have ``ncell * 4`` entries
    (4 corner vertices per cell, matching the cell-value order). Used to build a
    matplotlib triangulation for the animation (native metres = correct aspect).
    """
    if quadtree:
        nx = np.asarray(ds["mesh2d_node_x"].values, dtype=float)
        ny = np.asarray(ds["mesh2d_node_y"].values, dtype=float)
        fn = ds["mesh2d_face_nodes"]
        start = int(fn.attrs.get("start_index", 0))
        idx = np.clip(np.asarray(fn.values, dtype=np.int64) - start, 0, nx.size - 1)
        return nx[idx].ravel(), ny[idx].ravel(), idx.shape[0]
    cx = np.asarray(ds["corner_x"].values, dtype=float)
    cy = np.asarray(ds["corner_y"].values, dtype=float)
    vx = np.stack(
        [cx[:-1, :-1], cx[1:, :-1], cx[1:, 1:], cx[:-1, 1:]], axis=-1
    ).reshape(-1)
    vy = np.stack(
        [cy[:-1, :-1], cy[1:, :-1], cy[1:, 1:], cy[:-1, 1:]], axis=-1
    ).reshape(-1)
    ncell = (cx.shape[0] - 1) * (cx.shape[1] - 1)
    return vx, vy, ncell


def _add_basemap(ax, crs, basemap: str) -> None:
    """Add a contextily basemap behind the plot (best-effort; needs internet)."""
    try:
        import contextily as ctx
    except Exception:
        return
    sources = {
        "sat": ctx.providers.Esri.WorldImagery,
        "osm": ctx.providers.OpenStreetMap.Mapnik,
        "light": ctx.providers.CartoDB.Positron,
    }
    source = sources.get(basemap)
    if source is None:
        return
    epsg = crs.to_epsg() if crs is not None else None
    crs_arg = f"EPSG:{epsg}" if epsg else (crs.to_string() if crs else "EPSG:3857")
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    try:
        ctx.add_basemap(ax, crs=crs_arg, source=source, attribution=False, zorder=1)
    except Exception as e:
        logger.info("Could not add basemap: %s", e)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


def _face_values(ds: xr.Dataset, variable: str, tdim: Optional[str], itime: int):
    """Return per-face values with inactive/dry cells masked to NaN."""
    da = ds[variable]
    if tdim is not None and tdim in da.dims:
        n = ds.sizes[tdim]
        itime = max(0, min(itime, n - 1))
        da = da.isel({tdim: itime})
    z = np.asarray(da.values, dtype=float).ravel()
    z = np.where(np.abs(z) > 1.0e9, np.nan, z)  # guard against fill values
    if "msk" in ds:
        msk = np.asarray(ds["msk"].values, dtype=float).ravel()
        z = np.where(msk > 0, z, np.nan)
    if variable in ("h", "hmax"):
        z = np.where(z > 0.05, z, np.nan)  # hide dry cells
    return z


def _time_strings(ds: xr.Dataset, tdim: Optional[str]) -> List[str]:
    if tdim is None or tdim not in ds:
        return [""]
    times = pd.to_datetime(ds[tdim].values)
    return [t.strftime("%Y-%m-%d %H:%M:%S") for t in times]


def _refresh(tb) -> None:
    """Re-render the spatial overlay layer."""
    if tb.spatial_overlay is None:
        return
    app.map.layer[_G].layer["spatial"].set_data(tb.spatial_overlay)


def _apply_variable(tb, reset_time: bool = False, autoscale: bool = False) -> None:
    """Update the overlay values for the current variable/time selection."""
    if tb.spatial_ds is None or tb.spatial_overlay is None:
        return
    variable = app.gui.getvar(_G, "spatial_variable")
    tdim = _time_dim(variable)

    app.gui.setvar(_G, "spatial_time_strings", _time_strings(tb.spatial_ds, tdim))
    if reset_time:
        itime = ds_default_time_index(tb.spatial_ds, tdim)
        app.gui.setvar(_G, "spatial_time_index", itime)
    itime = app.gui.getvar(_G, "spatial_time_index")

    z = _face_values(tb.spatial_ds, variable, tdim, itime)
    tb.spatial_overlay.set_values(z)

    if autoscale:
        finite = z[np.isfinite(z)]
        if finite.size:
            cmin = float(np.nanpercentile(finite, 2))
            cmax = float(np.nanpercentile(finite, 98))
            if cmax <= cmin:
                cmax = cmin + 0.1
            app.gui.setvar(_G, "spatial_cmin", round(cmin, 2))
            app.gui.setvar(_G, "spatial_cmax", round(cmax, 2))

    _refresh(tb)


def ds_default_time_index(ds: xr.Dataset, tdim: Optional[str]) -> int:
    """Default to the last time step (final max / last instant)."""
    if tdim is None or tdim not in ds:
        return 0
    return int(ds.sizes[tdim]) - 1


# ----------------------------------------------------------------------
# GUI callbacks
# ----------------------------------------------------------------------


def select(*args: Any) -> None:
    """Activate the Spatial output tab: show the overlay, hide the points."""
    map.update()
    app.map.layer[_G].show()
    if "points" in app.map.layer[_G].layer:
        app.map.layer[_G].layer["points"].hide()
    tb = app.toolbox[_G]
    if tb.spatial_overlay is not None:
        _refresh(tb)
        app.map.layer[_G].layer["spatial"].show()


def _close_dataset(tb) -> None:
    """Close the open map dataset (releasing the file) and reset spatial state."""
    if getattr(tb, "spatial_ds", None) is not None:
        try:
            tb.spatial_ds.close()
        except Exception:
            pass
    tb.spatial_ds = None
    tb.spatial_overlay = None
    tb.spatial_crs = None
    tb.spatial_bounds = None
    if _G in app.map.layer and "spatial" in app.map.layer[_G].layer:
        app.map.layer[_G].layer["spatial"].clear()


def close_map_file(*args: Any) -> None:
    """Close the loaded map file so it is no longer locked (e.g. to re-run SFINCS)."""
    tb = app.toolbox[_G]
    if getattr(tb, "spatial_ds", None) is None:
        return
    _close_dataset(tb)
    app.gui.setvar(_G, "spatial_map_file_string", "File : ")
    app.gui.setvar(_G, "spatial_time_strings", [""])
    app.gui.setvar(_G, "spatial_time_index", 0)
    app.gui.window.update()


def load_map_file(*args: Any) -> None:
    """Load a SFINCS map file and render the default variable."""
    tb = app.toolbox[_G]
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select SFINCS map file", filter="*.nc"
    )
    if not full_name:
        return

    # Release any previously loaded file so it is not left locked on disk.
    _close_dataset(tb)

    try:
        ds = xr.open_dataset(full_name)
    except Exception as e:
        app.gui.window.dialog_warning(f"Could not open file:\n{e}")
        return

    quadtree = _is_quadtree(ds)
    if not quadtree and "corner_x" not in ds.variables:
        ds.close()
        app.gui.window.dialog_warning(
            "Unrecognised SFINCS map file: expected a quadtree (UGRID "
            "'mesh2d_*') or a regular grid ('corner_x' / 'corner_y')."
        )
        return

    crs = _file_crs(ds)
    if crs is None:
        crs = app.crs  # fall back to the application CRS
        app.gui.window.dialog_info(
            "No CRS found in the map file; using the current application CRS."
        )

    wb = app.gui.window.dialog_wait("Building spatial overlay ...")
    try:
        if quadtree:
            x3857, y3857, simplices = _build_geometry(ds, crs)
            xarr = np.asarray(ds["mesh2d_node_x"].values, dtype=float)
            yarr = np.asarray(ds["mesh2d_node_y"].values, dtype=float)
        else:
            x3857, y3857, simplices = _build_geometry_regular(ds, crs)
            xarr = np.asarray(ds["corner_x"].values, dtype=float)
            yarr = np.asarray(ds["corner_y"].values, dtype=float)
    except Exception as e:
        wb.close()
        ds.close()
        app.gui.window.dialog_warning(f"Could not build mesh overlay:\n{e}")
        return

    tb.spatial_ds = ds
    tb.spatial_crs = crs
    tb.spatial_overlay = QuadtreeMapOverlay(x3857, y3857, simplices)

    # Extent in lon/lat for zooming.
    nx = xarr
    ny = yarr
    to4326 = Transformer.from_crs(crs, 4326, always_xy=True)
    lon0, lat0 = to4326.transform(nx.min(), ny.min())
    lon1, lat1 = to4326.transform(nx.max(), ny.max())
    tb.spatial_bounds = (lon0, lat0, lon1, lat1)

    app.gui.setvar(_G, "spatial_map_file_string", "File : " + name + ext)
    _apply_variable(tb, reset_time=True, autoscale=True)
    wb.close()

    # Show and zoom.
    app.map.layer[_G].layer["points"].hide()
    app.map.layer[_G].layer["spatial"].show()
    _zoom_to_bounds(tb)


def select_variable(*args: Any) -> None:
    _apply_variable(app.toolbox[_G], reset_time=True, autoscale=True)
    app.gui.window.update()


def select_time(*args: Any) -> None:
    _apply_variable(app.toolbox[_G], reset_time=False, autoscale=False)


def select_colormap(*args: Any) -> None:
    _refresh(app.toolbox[_G])


def edit_cmin_cmax(*args: Any) -> None:
    _refresh(app.toolbox[_G])


def select_opacity(*args: Any) -> None:
    """Apply the selected transparency to the spatial overlay."""
    try:
        opacity = float(app.gui.getvar(_G, "spatial_opacity"))
    except Exception:
        opacity = 0.7
    if "spatial" in app.map.layer[_G].layer:
        app.map.layer[_G].layer["spatial"].set_opacity(opacity)


def animate(*args: Any) -> None:
    """Export an animation of the selected variable over all time steps.

    Builds the mesh triangulation once and updates only the per-cell colours per
    frame (matplotlib ``tripcolor`` + ``FuncAnimation``). Saves a GIF (Pillow)
    or MP4 (ffmpeg, if available) using the tab's current colormap/limits.
    """
    tb = app.toolbox[_G]
    if tb.spatial_ds is None:
        app.gui.window.dialog_info("Load a map file first.")
        return

    variable = app.gui.getvar(_G, "spatial_variable")
    tdim = _time_dim(variable)
    if tdim is None or tdim not in tb.spatial_ds.dims:
        app.gui.window.dialog_info(
            "The selected variable has no time dimension to animate."
        )
        return
    ds = tb.spatial_ds
    ntime = int(ds.sizes[tdim])
    if ntime < 2:
        app.gui.window.dialog_info("Only one time step available; nothing to animate.")
        return

    full_name, path, name, ext, fltr = app.gui.window.dialog_save_file(
        "Save animation", filter="*.mp4"
    )
    if not full_name:
        return

    import matplotlib
    import matplotlib.tri as mtri
    from matplotlib.animation import FFMpegWriter, PillowWriter
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    var_label = next((l for v, l, _ in _MAP_VARIABLES if v == variable), variable)
    cmap = app.gui.getvar(_G, "spatial_cmap")
    try:
        cmin = float(app.gui.getvar(_G, "spatial_cmin"))
        cmax = float(app.gui.getvar(_G, "spatial_cmax"))
    except Exception:
        cmin, cmax = 0.0, 2.0
    tstrings = _time_strings(ds, tdim)

    vx, vy, ncell = _native_vertices(ds, _is_quadtree(ds))
    base = np.arange(ncell) * 4
    triangles = np.vstack(
        [
            np.column_stack([base, base + 1, base + 2]),
            np.column_stack([base, base + 2, base + 3]),
        ]
    )
    triang = mtri.Triangulation(vx, vy, triangles)

    def facecolors(itime: int):
        z = _face_values(ds, variable, tdim, itime)
        return np.ma.masked_invalid(np.concatenate([z, z]))

    cmap_obj = matplotlib.cm.get_cmap(cmap).copy()
    cmap_obj.set_bad(alpha=0.0)

    basemap = app.gui.getvar(_G, "spatial_basemap")
    try:
        alpha = float(app.gui.getvar(_G, "spatial_opacity"))
    except Exception:
        alpha = 0.7
    if basemap == "none":
        alpha = 1.0

    # Standalone Agg figure (independent of the running Qt backend) so the
    # writer can render frames without a GUI event loop.
    fig = Figure(figsize=(8, 6))
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.set_axis_off()
    tpc = ax.tripcolor(
        triang,
        facecolors=facecolors(0),
        cmap=cmap_obj,
        vmin=cmin,
        vmax=cmax,
        shading="flat",
        alpha=alpha,
        zorder=2,
    )
    if basemap != "none":
        _add_basemap(ax, tb.spatial_crs, basemap)
    fig.colorbar(tpc, ax=ax, shrink=0.7, label=f"{var_label} (m)")
    title = ax.set_title(tstrings[0])

    # Choose writer by extension; fall back to GIF when ffmpeg is unavailable.
    want_mp4 = os.path.splitext(full_name)[1].lower() == ".mp4"
    if want_mp4 and FFMpegWriter.isAvailable():
        writer = FFMpegWriter(fps=5)
    else:
        if os.path.splitext(full_name)[1].lower() != ".gif":
            full_name = os.path.splitext(full_name)[0] + ".gif"
        writer = PillowWriter(fps=5)

    p = app.gui.window.dialog_progress("Rendering animation ...", 100)
    canceled = False
    try:
        # Drive the writer manually (no FuncAnimation → no GUI-timer conflict),
        # updating the progress bar per rendered frame.
        with writer.saving(fig, full_name, dpi=100):
            for i in range(ntime):
                tpc.set_array(facecolors(i))
                title.set_text(tstrings[i] if i < len(tstrings) else str(i))
                writer.grab_frame()
                p.set_text(f"Rendering animation: frame {i + 1} / {ntime}")
                p.set_value(int(100 * (i + 1) / ntime))
                if p.was_canceled():
                    canceled = True
                    break
    except Exception as e:
        p.close()
        app.gui.window.dialog_warning(f"Could not save animation:\n{e}")
        return
    p.close()

    if canceled:
        try:
            os.remove(full_name)
        except OSError:
            pass
        app.gui.window.dialog_info("Animation canceled.")
        return
    app.gui.window.dialog_info(f"Animation saved:\n{full_name}")


def _zoom_to_bounds(tb, buffer: float = 0.05) -> None:
    if tb.spatial_bounds is None:
        return
    x0, y0, x1, y1 = tb.spatial_bounds
    dx = x1 - x0
    dy = y1 - y0
    px = buffer * dx if dx > 0 else 0.05
    py = buffer * dy if dy > 0 else 0.05
    app.map.fit_bounds(x0 - px, y0 - py, x1 + px, y1 + py)
