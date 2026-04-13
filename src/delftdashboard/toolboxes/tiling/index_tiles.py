"""GUI callbacks for generating index tiles.

Create tiled web map index tiles from the active model grid.
"""

import shutil
import traceback
from pathlib import Path
from typing import Any

from cht_tiling import TiledWebMap

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the index tiles tab and set model-specific zmin/zmax defaults."""
    model = app.active_model
    if model is not None and model.name == "hurrywave_hmt":
        app.gui.setvar("tiling", "index_zmin", -99999.0)
        app.gui.setvar("tiling", "index_zmax", 0.0)
    else:
        app.gui.setvar("tiling", "index_zmin", -99999.0)
        app.gui.setvar("tiling", "index_zmax", 99999.0)
    map.update()


def _has_grid(component: Any) -> bool:
    """Return True if a hydromt grid component has actual data.

    Checks the private ``_data`` attribute directly to avoid triggering
    the lazy ``read()`` that would fail on a fresh, empty model.
    """
    data = getattr(component, "_data", None)
    if data is None:
        return False
    # An empty UgridDataset has no grid faces
    grid = getattr(data, "grid", None)
    if grid is None:
        return False
    n_face = getattr(grid, "n_face", None)
    return n_face is not None and n_face > 0


def _confirm_overwrite(folder: str) -> bool:
    """Ask the user to overwrite an existing tile folder; delete it on yes.

    Returns True if generation should proceed, False if the user cancelled.
    """
    p = Path(folder)
    if not p.exists():
        return True
    ok = app.gui.window.dialog_yes_no(
        f"Folder '{folder}' already exists. Overwrite?"
    )
    if not ok:
        return False
    try:
        shutil.rmtree(p)
    except OSError as e:
        app.gui.window.dialog_warning(f"Could not delete {folder}:\n{e}")
        return False
    return True


def generate_index_tiles(*args: Any) -> None:
    """Generate index tiles for the active model grid."""
    model = app.active_model
    path = "./tiling/indices"
    max_zoom = app.gui.getvar("tiling", "max_zoom")
    zoom_range = [0, max_zoom]
    zmin = app.gui.getvar("tiling", "index_zmin")
    zmax = app.gui.getvar("tiling", "index_zmax")

    if model.name == "sfincs_cht":
        grid = getattr(model.domain.grid, "data", None)
        if grid is None:
            app.gui.window.dialog_info("No model grid found. Please create a grid first.")
            return
        if not _confirm_overwrite(path):
            return
        dlg = app.gui.window.dialog_wait("Generating index tiles ...")
        twmi = TiledWebMap(
            path,
            type="data",
            parameter="index",
            data=grid,
            zoom_range=zoom_range,
        )
        twmi.make()
        dlg.close()

    elif model.name == "sfincs_hmt":
        if not _has_grid(model.domain.quadtree_grid):
            app.gui.window.dialog_info("No model grid found. Please create a grid first.")
            return
        if not _confirm_overwrite(path):
            return
        dlg = app.gui.window.dialog_wait("Generating index tiles ...")
        try:
            model.domain.quadtree_grid.create_index_tiles(
                root="./tiling",
                zoom_range=zoom_range,
            )
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating index tiles:\n{e}")
            return
        dlg.close()

    elif model.name == "hurrywave_hmt":
        if not _has_grid(model.domain.quadtree_grid):
            app.gui.window.dialog_info("No model grid found. Please create a grid first.")
            return

        # Initialise so they're always defined regardless of the branch taken below
        elevation_list = None
        z_range = None

        # Only need bathymetry when z_range actually constrains anything.
        # Effective sentinel range (~ ±99999) means "no masking", so skip
        # resolving the bathymetry datasets entirely.
        z_range_active = zmin > -90000.0 or zmax < 90000.0

        if z_range_active:
            if not app.selected_bathymetry_datasets:
                ok = app.gui.window.dialog_yes_no(
                    "No bathymetry datasets selected (this can be done in the ModelMaker toolbox). Index tiles will not be "
                    "masked by elevation. "
                    "Do you want to continue?"
                )
                if not ok:
                    return
            else:
                # Resolve dataset names to DataArrays via the standalone topo
                # catalog. We do this here (rather than letting
                # create_index_tiles do it via the model's data_catalog)
                # because:
                #   - For an opened model, the topo datasets are not registered
                #     in model.domain.data_catalog (only set up at "New model"
                #     time).
                #   - We don't want tiling to mutate the model catalog.
                # By passing fully-resolved entries (with "da" keys), the
                # create_index_tiles auto-conversion is bypassed.
                region = model.domain.quadtree_grid.exterior
                res = 40075016.686 / 256 / 2 ** zoom_range[1]
                elevation_list = app.topography_data_catalog.resolve_elevation_list(
                    app.selected_bathymetry_datasets, geom=region, res=res
                )
                z_range = [zmin, zmax]

        if not _confirm_overwrite(path):
            return

        dlg = app.gui.window.dialog_wait("Generating index tiles ...")
        try:
            model.domain.quadtree_grid.create_index_tiles(
                root="./tiling",
                elevation_list=elevation_list,
                z_range=z_range,
                zoom_range=zoom_range,
            )
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(f"Error generating index tiles:\n{e}")
            return
        dlg.close()

    else:
        app.gui.window.dialog_info(f"Tiling not supported for {model.name}")


def edit_variables(*args: Any) -> None:
    """Handle variable editing events (placeholder)."""
