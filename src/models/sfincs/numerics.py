# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select(*args):
    pass


def set_variables(*args):
    # All variables will be set
    ddb.model["sfincs"].set_model_variables()


def set_theta(*args):
    #    models.model["sfincs"].set_model_variables()
    #    # OR:
    ddb.model["sfincs"].domain.input.theta = ddb.gui.variables.var["sfincs"]["theta"]["value"]
