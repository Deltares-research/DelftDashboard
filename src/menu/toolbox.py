# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb
from operations.toolbox import select_toolbox

def select(toolbox_name):
    select_toolbox(toolbox_name)
    # ddb.active_toolbox = ddb.toolbox[toolbox_name]
    # ddb.active_toolbox.select()
