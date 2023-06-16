from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_active"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_mode("active")


def set_variables(*args):
    app.model["sfincs_hmt"].set_model_variables()
