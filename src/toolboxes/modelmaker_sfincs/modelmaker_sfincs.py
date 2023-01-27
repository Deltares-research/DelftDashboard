# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb_toolbox import GenericToolbox
from ddb import ddb

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Maker"
        print("Toolbox " + self.name + " added!")

#        self.initialize_domain()
#        self.set_gui_variables()

    def save(self):
        pass

    def load(self):
        pass

    def plot(self):
        pass

    def set_gui_variables(self):

        group = "sfincs"

        for var_name in vars(self.domain.input):
            ddb.gui.setvar(group, var_name, getattr(self.domain.input, var_name))

        ddb.gui.setvar(group, "tref", datetime.datetime(2000, 1, 1))
        ddb.gui.setvar(group, "tstart", datetime.datetime(2000, 1, 1))
        ddb.gui.setvar(group, "tstop", datetime.datetime(2000, 1, 3))

        ddb.gui.setvar(group, "roughness_type", "landsea")

        # Now set some extra variables needed for SFINCS GUI
        ddb.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        ddb.gui.setvar(group, "input_options_values", ["bin", "asc"])

        ddb.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        ddb.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])


    def set_input_variable(self, gui_variable, value):

        pass

def draw_rectangle():
    toolbox = ddb.toolbox["modelmaker_sfincs"]

    pass
