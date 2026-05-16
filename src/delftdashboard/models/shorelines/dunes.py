from delftdashboard.app import app

_MODEL = "shorelines"


def select(*args):
    app.model[_MODEL].select_layer("dunes")


def set_model_variables(*args):
    app.model[_MODEL].set_model_variables()


def add_dune_point_on_map(*args):
    app.model[_MODEL].add_dune_point_on_map()


def delete_dune(*args):
    app.model[_MODEL].delete_dune()


def load_dunes(*args):
    app.model[_MODEL].load_dunes()


def save_dunes(*args):
    app.model[_MODEL].save_feature("dunes")


def select_dune_from_list(*args):
    app.model[_MODEL].select_dune_from_list(*args)


def edit_dune_parameter(*args):
    app.model[_MODEL].edit_dune_parameter()


def dune_selected_from_map(*args):
    app.model[_MODEL].select_dune_from_map(*args)
