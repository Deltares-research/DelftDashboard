from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()

def edit(*args):
    app.model["fiat"].set_model_variables()

def test_svi(*args):
    print("Test")