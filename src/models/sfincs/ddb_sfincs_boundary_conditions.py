# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select():
    ddb.gui.main_window.update_active_tab()


def set_variables():
    # All variables will be set
    ddb.model["sfincs"].set_model_variables()
    ddb.main_window.update_active_tab()

def draw_boundary_spline():
    map.ol_map.draw_polyline("sfincs", "boundary_spline")
