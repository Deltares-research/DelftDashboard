# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def open_info(*args):
    app.gui.window.dialog_info(
        text="For polygon data select \"intersection\". For point data select \"nearest\" as method.",
        title="Method selection",
    )
