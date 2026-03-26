from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
    app.map.layer["hurrywave_hmt"].layer["grid"].activate()
    app.map.layer["hurrywave_hmt"].layer["mask"].activate()


def set_model_variables(*args):
    app.model["hurrywave_hmt"].set_model_variables()
