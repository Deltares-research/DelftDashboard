from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].set_activity(True)
    app.map.layer["sfincs_hmt"].layer["mask_active"].set_activity(True)
    app.map.layer["sfincs_hmt"].layer["mask_bound_wlev"].set_activity(True)
    app.map.layer["sfincs_hmt"].layer["mask_bound_outflow"].set_activity(True)


def set_variables(*args):
    app.model["sfincs_hmt"].set_model_variables()
