from delftdashboard.app import app

_MODEL = "shorelines"


def select():
    app.map.update()


def set_model_variables():
    app.model[_MODEL].set_model_variables()

