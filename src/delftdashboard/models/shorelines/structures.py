from delftdashboard.app import app

_MODEL = "shorelines"


def select(*args):
    app.model[_MODEL].select_layer("structures")


def set_model_variables(*args):
    app.model[_MODEL].set_model_variables()


def draw_structures(*args):
    app.model[_MODEL].draw_feature("structures")


def delete_structures(*args):
    app.model[_MODEL].delete_feature("structures")


def load_structures(*args):
    app.model[_MODEL].load_xy_feature("structures")


def save_structures(*args):
    app.model[_MODEL].save_feature("structures")


def draw_revetments(*args):
    app.model[_MODEL].draw_feature("revetments")


def delete_revetments(*args):
    app.model[_MODEL].delete_feature("revetments")


def load_revetments(*args):
    app.model[_MODEL].load_xy_feature("revetments")


def save_revetments(*args):
    app.model[_MODEL].save_feature("revetments")


def structures_created(gdf, index=None, id=None):
    app.model[_MODEL].feature_created("structures", gdf, index, id)


def structures_modified(gdf, index=None, id=None):
    app.model[_MODEL].feature_modified("structures", gdf, index, id)


def structures_selected(index=None, id=None):
    app.model[_MODEL].feature_selected("structures", None, index, id)


def revetments_created(gdf, index=None, id=None):
    app.model[_MODEL].feature_created("revetments", gdf, index, id)


def revetments_modified(gdf, index=None, id=None):
    app.model[_MODEL].feature_modified("revetments", gdf, index, id)


def revetments_selected(index=None, id=None):
    app.model[_MODEL].feature_selected("revetments", None, index, id)
