from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
    app.map.layer["sfincs_hmt"].layer["cross_sections"].set_mode("active")


def edit(*args):
    app.model["sfincs_hmt"].set_model_variables()
