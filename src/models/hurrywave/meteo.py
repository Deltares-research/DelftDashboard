# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select(*args):
    # De-activate existing layers
    ddb.update_map()

def edit(*args):
    ddb.model["hurrywave"].set_model_variables()
