from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_TB].layer["mask_boundary"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()


def deselect(*args):
    if app.toolbox[_TB].boundary_polygon_changed and len(app.toolbox[_TB].boundary_polygon) > 0:
        ok = app.gui.window.dialog_yes_no(
            "Your polygons have changed. Would you like to save the changes?")
        if ok:
            save_boundary_polygon()


def draw_boundary_polygon(*args):
    app.map.layer[_TB].layer["mask_boundary"].crs = app.crs
    app.map.layer[_TB].layer["mask_boundary"].draw()


def delete_boundary_polygon(*args):
    if len(app.toolbox[_TB].boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "boundary_polygon_index")
    gdf = app.map.layer[_TB].layer["mask_boundary"].delete_feature(index)
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True
    if index > len(app.toolbox[_TB].boundary_polygon) - 1:
        app.gui.setvar(_TB, "boundary_polygon_index", len(app.toolbox[_TB].boundary_polygon) - 1)
    update()


def load_boundary_polygon(*args):
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select boundary polygon file ...", filter="*.geojson")
    if not full_name:
        return
    append = False
    if app.gui.getvar(_TB, "nr_boundary_polygons"):
        append = app.gui.window.dialog_yes_no("Add to existing boundary polygons?", " ")
    app.toolbox[_TB].read_boundary_polygon(full_name, append)
    app.toolbox[_TB].plot_boundary_polygon()
    if append:
        app.toolbox[_TB].boundary_polygon_changed = True
    else:
        save_boundary_polygon()
    update()


def save_boundary_polygon(*args):
    app.gui.window.dialog_fade_label("Saving boundary polygons to boundary.geojson ...")
    app.toolbox[_TB].write_boundary_polygon()
    app.toolbox[_TB].boundary_polygon_changed = False


def select_boundary_polygon(*args):
    index = args[0]
    feature_id = app.toolbox[_TB].boundary_polygon.loc[index, "id"]
    app.map.layer[_TB].layer["mask_boundary"].activate_feature(feature_id)


def boundary_polygon_created(gdf, index, id):
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True
    nrp = len(app.toolbox[_TB].boundary_polygon)
    app.gui.setvar(_TB, "boundary_polygon_index", nrp - 1)
    update()


def boundary_polygon_modified(gdf, index, id):
    app.toolbox[_TB].boundary_polygon = gdf
    app.toolbox[_TB].boundary_polygon_changed = True


def boundary_polygon_selected(index):
    app.gui.setvar(_TB, "boundary_polygon_index", index)
    update()


def update():
    nrp = len(app.toolbox[_TB].boundary_polygon)
    app.gui.setvar(_TB, "nr_boundary_polygons", nrp)
    app.gui.setvar(_TB, "boundary_polygon_names", [str(ip + 1) for ip in range(nrp)])
    app.gui.window.update()


def update_mask(*args):
    app.toolbox[_TB].update_mask()


def cut_inactive_cells(*args):
    app.toolbox[_TB].cut_inactive_cells()
