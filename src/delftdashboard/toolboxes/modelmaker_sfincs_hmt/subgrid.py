from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")


def edit_nr_subgrid_pixels(*args):
    subgrid_buffer_cells = app.gui.getvar(
        "modelmaker_sfincs_hmt", "nr_subgrid_pixels"
    ) * app.gui.getvar("modelmaker_sfincs_hmt", "bathymetry_dataset_buffer_cells")
    app.gui.setvar(
        "modelmaker_sfincs_hmt", "subgrid_buffer_cells", subgrid_buffer_cells
    )


def generate_subgrid(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_subgrid()
