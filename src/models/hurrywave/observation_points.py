# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select(*args):
    ddb.update_map()
    ddb.map.layer["hurrywave"].layer["observation_points"].set_mode("active")

def edit(*args):
    ddb.model["hurrywave"].set_model_variables()
