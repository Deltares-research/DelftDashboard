# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb

def select_dataset(option):
    ddb.background_topography = option
    ddb.background_topography_layer.update()
    ddb.gui.setvar("menu", "active_topography_name", option)
