from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"


def select(*args):
    map.update()


def edit(*args):
    pass


def generate_waveblocking(*args):
    app.toolbox[_TB].generate_waveblocking()
