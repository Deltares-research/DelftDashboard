from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
