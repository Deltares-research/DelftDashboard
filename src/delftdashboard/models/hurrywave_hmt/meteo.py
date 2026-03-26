from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()


def edit(*args):
    app.model["hurrywave_hmt"].set_model_variables()
