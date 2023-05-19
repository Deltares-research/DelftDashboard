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


def set_variables(*args):
    # All variables will be set
    app.model["sfincs"].set_model_variables()


def set_theta(*args):
    #    models.model["sfincs"].set_model_variables()
    #    # OR:
    app.model["sfincs"].domain.input.theta = app.gui.variables.var["sfincs"]["theta"]["value"]
