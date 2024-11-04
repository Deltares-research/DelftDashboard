# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app

def select_dataset(option):
    app.gui.setvar("view_settings", "topography_dataset", option)
    app.map.layer["main"].layer["background_topography"].update()
    app.gui.setvar("menu", "active_topography_name", option) # still change this to in menu
    app.gui.window.update() # Make sure the other dataset are unchecked
    
