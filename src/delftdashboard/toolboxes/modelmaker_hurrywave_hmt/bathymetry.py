from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()


def generate_bathymetry(*args):
    app.toolbox[_TB].generate_bathymetry()


def edit(*args):
    pass


def info(*args):
    pass
