# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def setup_max_dist_damages(*args):
    max_dist_damages = app.gui.getvar("fiat", "max_dist_damages")
    app.active_model.domain.exposure_vm.set_max_dist_damages(max_dist_damages)


def setup_method_damages(*args):
    method_damages = app.gui.getvar("fiat", "method_damages")
    app.active_model.domain.exposure_vm.set_method_damages(method_damages)