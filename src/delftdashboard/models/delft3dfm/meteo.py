# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
import ast

def select(*args):
    # De-activate existing layers
    map.update()

def set_model_variables(*args):
    # Convert string list to list
    vars = ['wind.cdbreakpoints', 'wind.windspeedbreakpoints']
    for i,v in enumerate(vars):
        if isinstance(app.gui.variables['delft3dfm'][v]['value'], str):
            app.gui.variables['delft3dfm'][v]['value'] = ast.literal_eval(app.gui.variables['delft3dfm'][v]['value'])

    app.model["delft3dfm"].set_input_variables()
