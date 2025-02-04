# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations.toolbox import GenericToolbox

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Tiling"

    def initialize(self):
        group = "tiling"
        # Make a list of 0 to 23
        lst = list(range(24))
        # And convert to strings
        lststr = [str(i) for i in lst]
        app.gui.setvar(group, "zoom_levels", lst)
        app.gui.setvar(group, "zoom_levels_text", lststr)
        app.gui.setvar(group, "max_zoom", 13)

    def set_layer_mode(self, mode):
        pass

    def add_layers(self):
        pass
