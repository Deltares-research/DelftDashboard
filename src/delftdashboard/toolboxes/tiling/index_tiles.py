"""GUI callbacks for generating index tiles.

Create tiled web map index tiles from the active model grid.
"""

from typing import Any

from cht_tiling import TiledWebMap

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the index tiles tab."""
    map.update()


def generate_index_tiles(*args: Any) -> None:
    """Generate index tiles for the active model grid."""
    model = app.active_model

    if model.name == "sfincs_cht":
        dlg = app.gui.window.dialog_wait("Generating index tiles ...")

        grid = model.domain.grid.data
        path = "./tiling/indices"
        max_zoom = app.gui.getvar("tiling", "max_zoom")
        zoom_range = [0, max_zoom]

        # Create index tiles
        twmi = TiledWebMap(
            path,
            type="data",
            parameter="index",
            data=grid,
            zoom_range=zoom_range,
        )
        twmi.make()

        dlg.close()

    elif model.name == "hurrywave":
        dlg = app.gui.window.dialog_wait("Generating index tiles ...")

        grid = model.domain.grid.data.xuds
        path = "./tiling/indices"
        max_zoom = app.gui.getvar("tiling", "max_zoom")
        zoom_range = [0, max_zoom]

        # Create index tiles
        twmi = TiledWebMap(
            path,
            type="data",
            parameter="index",
            data=grid,
            zoom_range=zoom_range,
            topo_path=r"c:\work\delftdashboard\data\bathymetry\gebco_2024",
        )
        twmi.make()

        dlg.close()

    else:
        app.gui.window.dialog_message(f"Tiling not supported for {model.name}")


def edit_variables(*args: Any) -> None:
    """Handle variable editing events (placeholder)."""
