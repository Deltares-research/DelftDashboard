from delftdashboard.app import app

_MODEL = "shorelines"


def select():
    app.model[_MODEL].select_layer("nourishments")


def set_model_variables():
    app.model[_MODEL].set_model_variables()


def draw_nourishments():
    app.model[_MODEL].draw_feature("nourishments")


def delete_nourishments():
    app.model[_MODEL].delete_feature("nourishments")


def load_nourishments():
    app.model[_MODEL].load_xy_feature("nourishments")


def nourishments_created(gdf, index=None, id=None):
    app.model[_MODEL].feature_created("nourishments", gdf, index, id)


def nourishments_modified(gdf, index=None, id=None):
    app.model[_MODEL].feature_modified("nourishments", gdf, index, id)


def nourishments_selected(gdf, index=None, id=None):
    app.model[_MODEL].feature_selected("nourishments", gdf, index, id)

