"""GUI callbacks for generating topobathy tiles."""

import os
import traceback

from cht_tiling import TiledWebMap

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    """Activate the tiling tab."""
    map.update()


def generate_topobathy_tiles(*args):
    """Generate topobathy tiles for the active model."""
    model = app.active_model
    index_path = "./tiling/indices"
    path = "./tiling/topobathy"

    if not os.path.exists(index_path):
        app.gui.window.dialog_message("Please generate index tiles first !")
        return

    if model.name not in ("sfincs_cht", "sfincs_hmt"):
        app.gui.window.dialog_message(f"Tiling not supported for {model.name}")
        return

    dlg = app.gui.window.dialog_wait("Generating topo/bathy tiles ...")
    try:
        dem_list = app.selected_bathymetry_datasets
        twmb = TiledWebMap(
            path,
            type="data",
            parameter="elevation",
            data=dem_list,
            data_catalog=app.topography_data_catalog.catalog,
            index_path=index_path,
        )
        twmb.make()
    except Exception as e:
        traceback.print_exc()
        dlg.close()
        app.gui.window.dialog_warning(f"Error generating topobathy tiles:\n{e}")
        return
    dlg.close()


def edit_variables(*args):
    """Placeholder for variable editing."""
