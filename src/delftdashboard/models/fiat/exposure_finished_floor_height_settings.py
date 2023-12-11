# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def setup_max_dist_gfh(*args):
    max_dist_gfh = app.gui.getvar("fiat", "max_dist_gfh")
    app.active_model.domain.exposure_vm.set_max_dist_gfh(max_dist_gfh)


def setup_method_gfh(*args):
    method_gfh = app.gui.getvar("fiat", "method_gfh")
    app.active_model.domain.exposure_vm.set_method_gfh(method_gfh)