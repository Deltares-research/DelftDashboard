from delftdashboard.app import app

_MODEL = "shorelines"


def select(*args):
    app.model[_MODEL].plot()


def set_model_variables(*args):
    app.model[_MODEL].set_model_variables()
