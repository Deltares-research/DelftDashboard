from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_hurrywave_hmt"
_MODEL = "hurrywave_hmt"


def select(*args):
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()


def create_boundary_points(*args):
    dlg = app.gui.window.dialog_wait("Making boundary points ...")

    bc = app.model[_MODEL].domain.boundary_conditions
    if bc.nr_points > 0:
        ok = app.gui.window.dialog_ok_cancel(
            "Existing boundary points will be overwritten! Continue?",
            title="Warning")
        if not ok:
            dlg.close()
            return

    bnd_dist = app.gui.getvar(_MODEL, "boundary_dx")
    bc.get_boundary_points_from_mask(bnd_dist=bnd_dist)
    gdf = bc.gdf
    app.map.layer[_MODEL].layer["boundary_points"].set_data(gdf, 0)
    bc.set_uniform(hs=1.0, tp=8.0, wd=45.0, ds=20.0)
    bc.write()

    dlg.close()
