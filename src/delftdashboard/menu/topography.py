# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app

def select_dataset(option):
    app.background_topography = option
    app.background_topography_layer.update()
    app.gui.setvar("menu", "active_topography_name", option)
