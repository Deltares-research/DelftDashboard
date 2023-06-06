
from delftdashboard.app import app


def select(*args):
    pass


def set_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()
