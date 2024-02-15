# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app


def update_parameters(parameter: str):
    try:
        buildings, roads = app.active_model.domain.update_model(parameter)
    except Exception as e:
        app.gui.window.dialog_warning(
            str(e),
            "Not ready to build a FIAT model",
        )
        return

    if buildings is not None:
        app.active_model.buildings = buildings
    if roads is not None:
        app.active_model.roads = roads