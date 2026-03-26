import numpy as np
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_GROUP = "hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def _bc():
    return app.model[_MODEL].domain.boundary_conditions


def select(*args):
    map.update()
    app.map.layer[_MODEL].layer["boundary_points"].activate()
    update_conditions()
    update_list()


def write():
    _bc().write()


def add_boundary_point_on_map(*args):
    app.map.click_point(point_clicked)


def point_clicked(x, y):
    hs = app.gui.getvar(_GROUP, "boundary_hm0")
    tp = app.gui.getvar(_GROUP, "boundary_tp")
    wd = app.gui.getvar(_GROUP, "boundary_wd")
    ds = app.gui.getvar(_GROUP, "boundary_ds")
    _bc().add_point(x, y, hs=hs, tp=tp, wd=wd, ds=ds)
    index = _bc().nr_points - 1
    gdf = _bc().gdf
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "nr_boundary_points", _bc().nr_points)
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    update_list()
    update_conditions()
    write()


def select_boundary_point_from_list(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    app.map.layer[_MODEL].layer["boundary_points"].select_by_index(index)
    update_conditions()


def select_boundary_point_from_map(*args):
    index = args[0]["id"]
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    update_conditions()
    app.gui.window.update()


def delete_point_from_list(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    _bc().delete([index])
    gdf = _bc().gdf
    index = max(min(index, _bc().nr_points - 1), 0)
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, index)
    app.gui.setvar(_GROUP, "active_boundary_point", index)
    app.gui.setvar(_GROUP, "nr_boundary_points", _bc().nr_points)
    update_conditions()
    update_list()
    write()


def create_boundary_points(*args):
    dlg = app.gui.window.dialog_wait("Making boundary points ...")

    if _bc().nr_points > 0:
        ok = app.gui.window.dialog_ok_cancel(
            "Existing boundary points will be overwritten! Continue?",
            title="Warning"
        )
        if not ok:
            dlg.close()
            return

    bnd_dist = app.gui.getvar(_GROUP, "boundary_dx")
    _bc().get_boundary_points_from_mask(bnd_dist=bnd_dist)
    gdf = _bc().gdf
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, 0)

    # Apply uniform default conditions and write
    _bc().set_uniform(hs=1.0, tp=8.0, wd=45.0, ds=20.0)
    write()

    dlg.close()
    update_conditions()
    update_list()


def update_list():
    nr = _bc().nr_points
    names = []
    gdf = _bc().gdf
    if len(gdf) > 0 and "name" in gdf.columns:
        names = list(gdf["name"].values)
    app.gui.setvar(_GROUP, "boundary_point_names", names)
    app.gui.setvar(_GROUP, "nr_boundary_points", nr)
    app.gui.window.update()


def update_conditions():
    bc = _bc()
    if bc.forcing != "timeseries" or bc.nr_points == 0:
        return
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    data = bc.data
    if "hs" not in data or data["hs"].sizes.get("index", 0) <= index:
        return
    app.gui.setvar(_GROUP, "boundary_hm0",
                   float(data["hs"].isel(index=index, time=0)))
    app.gui.setvar(_GROUP, "boundary_tp",
                   float(data["tp"].isel(index=index, time=0)))
    app.gui.setvar(_GROUP, "boundary_wd",
                   float(data["wd"].isel(index=index, time=0)))
    app.gui.setvar(_GROUP, "boundary_ds",
                   float(data["ds"].isel(index=index, time=0)))


def select_boundary_forcing(*args):
    _bc().forcing = args[0]


def _set_parameter_at_point(var, index, value):
    """Set a scalar value for all time steps of *var* at point *index*."""
    bc = _bc()
    if var not in bc.data:
        return
    vals = bc.data[var].values.copy()
    vals[:, index] = value
    bc._data[var].values[:] = vals


def edit_hm0(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    _set_parameter_at_point("hs", index, args[0])
    write()


def edit_tp(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    _set_parameter_at_point("tp", index, args[0])
    write()


def edit_wd(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    _set_parameter_at_point("wd", index, args[0])
    write()


def edit_ds(*args):
    index = app.gui.getvar(_GROUP, "active_boundary_point")
    _set_parameter_at_point("ds", index, args[0])
    write()


def apply_to_all(*args):
    hs = app.gui.getvar(_GROUP, "boundary_hm0")
    tp = app.gui.getvar(_GROUP, "boundary_tp")
    wd = app.gui.getvar(_GROUP, "boundary_wd")
    ds = app.gui.getvar(_GROUP, "boundary_ds")
    _bc().set_uniform(hs=hs, tp=tp, wd=wd, ds=ds)
    write()
