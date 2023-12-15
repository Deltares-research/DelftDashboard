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
    dlg = app.gui.window.dialog_wait("\nCreating a FIAT model...")
    updated_exposure_output = app.active_model.domain.run_hydromt_fiat()
    app.active_model.updated_exposure = updated_exposure_output
    dlg.close()
    app.gui.window.dialog_info(
            f"A FIAT model is created in:\n{app.active_model.domain.fiat_model.root}",
            "FIAT model created",
        )

def edit(*args):
    app.active_model.set_model_variables()
