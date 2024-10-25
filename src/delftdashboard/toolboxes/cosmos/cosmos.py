# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.operations.toolbox import GenericToolbox

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "CoSMoS"

    def set_layer_mode(self, mode):
        pass

    def add_layers(self):
        pass
