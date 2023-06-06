from delftdashboard.app import app


def select(*args):
    pass


def set_variables(*args):
    app.model["sfincs_hmt"].set_model_variables()
