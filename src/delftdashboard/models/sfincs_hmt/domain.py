from delftdashboard.app import app


def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid and mask
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_include"].set_mode("active")
    app.map.layer["sfincs_hmt"].layer["mask_boundary"].set_mode("active")

def set_variables(*args):
    app.model[""].set_model_variables()
