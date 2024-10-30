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
        self.long_name = "Nesting"

    def initialize(self):

        group = "nesting"
        
        app.gui.setvar(group, "obs_point_prefix", "nest")

        app.gui.setvar(group, "detail_model_type", "")
        app.gui.setvar(group, "detail_model_file", "")
        app.gui.setvar(group, "detail_model_types", [])
        app.gui.setvar(group, "detail_model_type_long_names", [])
        app.gui.setvar(group, "detail_model_loaded", False)

        app.gui.setvar(group, "overall_model_type", "")
        app.gui.setvar(group, "overall_model_file", "")
        app.gui.setvar(group, "overall_model_types", [])
        app.gui.setvar(group, "overall_model_type_long_names", [])
        app.gui.setvar(group, "overall_model_loaded", False)

        app.gui.setvar(group, "water_level_correction", 0.0)

        
    def set_layer_mode(self, mode):
        pass

    def add_layers(self):
        pass
