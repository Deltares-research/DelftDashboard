from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_active"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].activate()
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].activate()


def set_variables(*args):
    app.model["sfincs_hmt"].set_model_variables()
