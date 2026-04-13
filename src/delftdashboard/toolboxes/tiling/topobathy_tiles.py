"""GUI callbacks for generating topobathy tiles."""

import os
import traceback

from delftdashboard.app import app
from delftdashboard.operations import map

from .index_tiles import _confirm_overwrite, _has_grid


def select(*args):
    """Activate the tiling tab."""
    map.update()


def generate_topobathy_tiles(*args):
    """Generate topobathy tiles for the active model."""
    model = app.active_model
    index_path = "./tiling/indices"
    path = "./tiling/topobathy"

    if not os.path.exists(index_path):
        app.gui.window.dialog_info("Please generate index tiles first !")
        return

    if model.name == "sfincs_hmt":
        if not _has_grid(model.domain.quadtree_grid):
            app.gui.window.dialog_info(
                "No model grid found. Please create a grid first."
            )
            return

        if not app.selected_bathymetry_datasets:
            app.gui.window.dialog_info(
                "No bathymetry datasets selected (this can be done in the "
                "ModelMaker toolbox)."
            )
            return

        # Resolve dataset names to DataArrays via the standalone topo
        # catalog. We do this here (rather than letting create_topobathy_tiles
        # fall back to the model's data_catalog) because:
        #   - For an opened model, the topo datasets are not registered in
        #     model.domain.data_catalog (only set up at "New model" time).
        #   - We don't want tiling to mutate the model catalog.
        # By passing fully-resolved entries (with "da" keys), the
        # create_topobathy_tiles auto-conversion is bypassed.
        max_zoom = app.gui.getvar("tiling", "max_zoom")
        zoom_range = [0, max_zoom]
        region = model.domain.quadtree_grid.exterior
        res = 40075016.686 / 256 / 2 ** zoom_range[1]
        elevation_list = app.topography_data_catalog.resolve_elevation_list(
            app.selected_bathymetry_datasets, geom=region, res=res
        )

        if not _confirm_overwrite(path):
            return

        dlg = app.gui.window.dialog_wait("Generating topo/bathy tiles ...")
        try:
            model.domain.quadtree_grid.create_topobathy_tiles(
                root="./tiling",
                elevation_list=elevation_list,
                zoom_range=zoom_range,
                index_path=index_path,
            )
        except Exception as e:
            traceback.print_exc()
            dlg.close()
            app.gui.window.dialog_warning(
                f"Error generating topobathy tiles:\n{e}"
            )
            return
        dlg.close()
        return

    app.gui.window.dialog_info(f"Topo/bathy tiling not supported for {model.name}")


def edit_variables(*args):
    """Placeholder for variable editing."""
