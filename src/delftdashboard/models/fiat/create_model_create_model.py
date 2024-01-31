# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def create_model(*args):
    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        return

    dlg = app.gui.window.dialog_wait("\nCreating a FIAT model...")

    try:
        buildings, roads = app.active_model.domain.run_hydromt_fiat()
    except Exception as e:
        app.gui.window.dialog_warning(
            str(e),
            "Not ready to build a FIAT model",
        )
        dlg.close()
        return

    if buildings is not None:
        app.active_model.buildings = buildings
    if roads is not None:
        app.active_model.roads = roads

    # Set the unit for Exposure Data for visualization
    view_tab_unit = app.active_model.domain.fiat_model.exposure.unit
    app.gui.setvar("fiat", "view_tab_unit", view_tab_unit)

    dlg.close()
    app.gui.window.dialog_info(
        f"A FIAT model is created in:\n{app.active_model.domain.fiat_model.root}",
        "FIAT model created",
    )


def edit(*args):
    app.active_model.set_model_variables()
