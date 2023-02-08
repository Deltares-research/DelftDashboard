# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb import ddb

def select():
#    ddb.gui.update_tab()
    pass

def set_variables():
    ddb.model["sfincs"].set_model_variables()
    ddb.gui.update_tab()
