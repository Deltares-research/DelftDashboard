# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()
    # Show the grid and mask
    ddb.map.layer["hurrywave"].layer["grid"].set_mode("active")
    ddb.map.layer["hurrywave"].layer["mask_include"].set_mode("active")
    ddb.map.layer["hurrywave"].layer["mask_boundary"].set_mode("active")

def set_variables(*args):
    ddb.model["hurrywave"].set_input_variables()
