from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()

def edit(*args):
    app.model["fiat"].set_model_variables()

def add_svi(*args):
    print("add_svi")

def toggle_svi(*args):
    print("toggle_svi")

def toggle_equity(*args):
    print("toggle_equity")
