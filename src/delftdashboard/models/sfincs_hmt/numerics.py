# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app


def select(*args):
    pass


def set_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()


def set_theta(*args):
    #    models.model["sfincs_hmt"].set_model_variables()
    #    # OR:
    app.model["sfincs_hmt"].domain.input.theta = app.gui.variables.var["sfincs_hmt"][
        "theta"
    ]["value"]
