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

def draw_domain(*args):
    toolbox = app.toolbox["modelmaker_sfincs_cht"]    
    pass
    
