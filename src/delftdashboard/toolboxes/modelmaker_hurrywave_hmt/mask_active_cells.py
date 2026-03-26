from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_TB].layer["mask_include"].activate()
    app.map.layer[_TB].layer["mask_exclude"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()


def deselect(*args):
    changed = False
    if app.toolbox[_TB].include_polygon_changed and len(app.toolbox[_TB].include_polygon) > 0:
        changed = True
    if app.toolbox[_TB].exclude_polygon_changed and len(app.toolbox[_TB].exclude_polygon) > 0:
        changed = True
    if changed:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?")
        if ok:
            if app.toolbox[_TB].include_polygon_changed and len(app.toolbox[_TB].include_polygon) > 0:
                save_include_polygon()
            if app.toolbox[_TB].exclude_polygon_changed and len(app.toolbox[_TB].exclude_polygon) > 0:
                save_exclude_polygon()


def draw_include_polygon(*args):
    app.map.layer[_TB].layer["mask_include"].crs = app.crs
    app.map.layer[_TB].layer["mask_include"].draw()


def delete_include_polygon(*args):
    if len(app.toolbox[_TB].include_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "include_polygon_index")
    gdf = app.map.layer[_TB].layer["mask_include"].delete_feature(index)
    app.toolbox[_TB].include_polygon = gdf
    if index > len(app.toolbox[_TB].include_polygon) - 1:
        app.gui.setvar(_TB, "include_polygon_index", len(app.toolbox[_TB].include_polygon) - 1)
    update()


def load_include_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select include polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_include_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing include polygons?", " ")
    app.toolbox[_TB].read_include_polygon(full_name, append)
    app.toolbox[_TB].plot_include_polygon()
    if append:
        app.toolbox[_TB].include_polygon_changed = True
    else:
        save_include_polygon()
    update()


def save_include_polygon(*args):
    app.gui.window.dialog_fade_label("Saving include polygons to include.geojson ...")
    app.toolbox[_TB].write_include_polygon()
    app.toolbox[_TB].include_polygon_changed = False


def select_include_polygon(*args):
    index = args[0]
    feature_id = app.toolbox[_TB].include_polygon.loc[index, "id"]
    app.map.layer[_TB].layer["mask_include"].activate_feature(feature_id)


def include_polygon_created(gdf, index, id):
    app.toolbox[_TB].include_polygon = gdf
    nrp = len(app.toolbox[_TB].include_polygon)
    app.gui.setvar(_TB, "include_polygon_index", nrp - 1)
    app.toolbox[_TB].include_polygon_changed = True
    update()


def include_polygon_modified(gdf, index, id):
    app.toolbox[_TB].include_polygon = gdf
    app.toolbox[_TB].include_polygon_changed = True


def include_polygon_selected(index):
    app.gui.setvar(_TB, "include_polygon_index", index)
    update()


def draw_exclude_polygon(*args):
    app.map.layer[_TB].layer["mask_exclude"].draw()


def delete_exclude_polygon(*args):
    if len(app.toolbox[_TB].exclude_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    gdf = app.map.layer[_TB].layer["mask_exclude"].delete_feature(index)
    app.toolbox[_TB].exclude_polygon = gdf
    if index > len(app.toolbox[_TB].exclude_polygon) - 1:
        app.gui.setvar(_TB, "exclude_polygon_index", len(app.toolbox[_TB].exclude_polygon) - 1)
    update()


def load_exclude_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select exclude polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_exclude_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing exclude polygons?", " ")
    app.toolbox[_TB].read_exclude_polygon(full_name, append)
    app.toolbox[_TB].plot_exclude_polygon()
    if append:
        app.toolbox[_TB].exclude_polygon_changed = True
    else:
        save_exclude_polygon()
    update()


def save_exclude_polygon(*args):
    app.gui.window.dialog_fade_label("Saving exclude polygons to exclude.geojson ...")
    app.toolbox[_TB].write_exclude_polygon()
    app.toolbox[_TB].exclude_polygon_changed = False


def select_exclude_polygon(*args):
    index = args[0]
    feature_id = app.toolbox[_TB].exclude_polygon.loc[index, "id"]
    app.map.layer[_TB].layer["mask_exclude"].activate_feature(feature_id)


def exclude_polygon_created(gdf, index, id):
    app.toolbox[_TB].exclude_polygon = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon)
    app.gui.setvar(_TB, "exclude_polygon_index", nrp - 1)
    app.toolbox[_TB].exclude_polygon_changed = True
    update()


def exclude_polygon_modified(gdf, index, id):
    app.toolbox[_TB].exclude_polygon = gdf
    app.toolbox[_TB].exclude_polygon_changed = True


def exclude_polygon_selected(index):
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    update()


def update():
    nrp = len(app.toolbox[_TB].include_polygon)
    app.gui.setvar(_TB, "nr_include_polygons", nrp)
    app.gui.setvar(_TB, "include_polygon_names", [str(ip + 1) for ip in range(nrp)])

    nrp = len(app.toolbox[_TB].exclude_polygon)
    app.gui.setvar(_TB, "nr_exclude_polygons", nrp)
    app.gui.setvar(_TB, "exclude_polygon_names", [str(ip + 1) for ip in range(nrp)])

    app.gui.window.update()


def update_mask(*args):
    app.toolbox[_TB].update_mask()


def cut_inactive_cells(*args):
    app.toolbox[_TB].cut_inactive_cells()
