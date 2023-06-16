from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")


def select_infiltration_method(*args):
    pass

def select_cn_method(*args):
    pass

def select_qinf_method(*args):
    pass


def generate_infiltration(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_infiltration()
