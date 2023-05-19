# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations.toolbox import select_toolbox

def select(toolbox_name):
    select_toolbox(toolbox_name)
    # app.active_toolbox = app.toolbox[toolbox_name]
    # app.active_toolbox.select()
