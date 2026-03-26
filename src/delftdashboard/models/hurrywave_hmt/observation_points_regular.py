from delftdashboard.app import app
from delftdashboard.operations import map

_GROUP = "hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_MODEL].layer["observation_points_regular"].activate()
    update()


def edit(*args):
    app.model[_MODEL].set_model_variables()


def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="hurrywave.obs",
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.read()
        gdf = app.model[_MODEL].domain.observation_points.gdf
        app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, 0)
        app.gui.setvar(_GROUP, "active_observation_point_regular", 0)
        update()


def save(*args):
    map.reset_cursor()
    file_name = app.model[_MODEL].domain.config.get("obsfile")
    if not file_name:
        file_name = "hurrywave.obs"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=file_name,
                                          filter="*.obs",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model[_MODEL].domain.config.set("obsfile", rsp[2])
        app.model[_MODEL].domain.observation_points.write()


def update():
    gdf = app.model[_MODEL].domain.observation_points.gdf
    names = list(gdf["name"].values) if len(gdf) > 0 else []
    app.gui.setvar(_GROUP, "observation_point_names_regular", names)
    app.gui.setvar(_GROUP, "nr_observation_points_regular", len(gdf))
    app.gui.window.update()


def add_observation_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    name, okay = app.gui.window.dialog_string("Edit name for new observation point")
    if not okay:
        return
    if name in app.gui.getvar(_GROUP, "observation_point_names_regular"):
        app.gui.window.dialog_info("An observation point with this name already exists !")
        return
    app.model[_MODEL].domain.observation_points.add_point(x, y, name=name)
    index = len(app.model[_MODEL].domain.observation_points.gdf) - 1
    gdf = app.model[_MODEL].domain.observation_points.gdf
    app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    update()


def select_observation_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_regular")
    app.map.layer[_MODEL].layer["observation_points_regular"].select_by_index(index)


def select_observation_point_from_map_regular(*args):
    map.reset_cursor()
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    app.gui.window.update()


def delete_point_from_list(*args):
    map.reset_cursor()
    index = app.gui.getvar(_GROUP, "active_observation_point_regular")
    app.model[_MODEL].domain.observation_points.delete([index])
    gdf = app.model[_MODEL].domain.observation_points.gdf
    index = max(min(index, len(gdf) - 1), 0)
    app.map.layer[_MODEL].layer["observation_points_regular"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_observation_point_regular", index)
    update()
