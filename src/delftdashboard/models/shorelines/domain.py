from delftdashboard.app import app

_MODEL = "shorelines"


def select(*args):
    app.model[_MODEL].select_layer("coastline")


def set_model_variables(*args):
    app.model[_MODEL].set_model_variables()


def draw_coastline(*args):
    app.model[_MODEL].draw_feature("coastline")


def delete_coastline(*args):
    app.model[_MODEL].delete_feature("coastline")


def load_coastline(*args):
    app.model[_MODEL].load_xy_feature("coastline")


def save_coastline(*args):
    app.model[_MODEL].save_feature("coastline")


def coastline_created(gdf, index=None, id=None):
    app.model[_MODEL].feature_created("coastline", gdf, index, id)


def coastline_modified(gdf, index=None, id=None):
    app.model[_MODEL].feature_modified("coastline", gdf, index, id)


def coastline_selected(index=None, id=None):
    app.model[_MODEL].feature_selected("coastline", None, index, id)
