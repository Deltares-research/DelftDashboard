# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import datetime

from ddb_model import GenericModel
from ddb import ddb

#from cht.sfincs.sfincs import SFINCS
from hydromt_sfincs import SfincsModel

class Model(GenericModel):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "SFINCS"

        print("Model " + self.name + " added!")
        self.active_domain = 0

        self.initialize_domain()
        self.set_gui_variables()

    def open(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def plot(self):
        pass

    def set_gui_variables(self):

        group = "sfincs"

#        for var_name in vars(self.domain.input):
        for var_name in self.domain.config:
            ddb.gui.setvar(group, var_name, self.domain.config[var_name])
#                ddb.gui.setvar(group, var_name, getattr(self.domain.input, var_name))

        # # Loop through available input variables
        # gui.variables.add(group, "tstart",      self.domain.input.tstart,       minval=None,    maxval=None, errmsg="SFINCS start time must be greater than stop time")
        # gui.variables.add(group, "tstop",       self.domain.input.tstop,        minval=None,    maxval=None, errmsg="SFINCS start time must be greater than stop time")
        # gui.variables.add(group, "theta",       self.domain.input.theta,        minval=0.0,     maxval=1.0)
        # gui.variables.add(group, "huthresh",    self.domain.input.huthresh,     minval=0.0001,  maxval=0.5)
        # gui.variables.add(group, "inputformat", self.domain.input.inputformat)
        # gui.variables.add(group, "x0",          self.domain.input.x0)
        # gui.variables.add(group, "y0",          self.domain.input.y0)
        # gui.variables.add(group, "dx",          self.domain.input.dx)
        # gui.variables.add(group, "dy",          self.domain.input.dy)
        # gui.variables.add(group, "nmax",        self.domain.input.nmax)
        # gui.variables.add(group, "mmax",        self.domain.input.mmax)
        # gui.variables.add(group, "rotation",    self.domain.input.rotation)
        # gui.variables.add(group, "latitude",    self.domain.input.latitude)
        # gui.variables.add(group, "manning",     self.domain.input.manning)
        # gui.variables.add(group, "manning_land",     self.domain.input.manning_land)
        # gui.variables.add(group, "manning_sea",     self.domain.input.manning_sea)
        # gui.variables.add(group, "rgh_lev_land",     self.domain.input.rgh_lev_land)
        # gui.variables.add(group, "advection",     self.domain.input.advection)
        # gui.variables.add(group, "advlim",     self.domain.input.advlim)

        ddb.gui.setvar(group, "tref", datetime.datetime(2000, 1, 1))
        ddb.gui.setvar(group, "tstart", datetime.datetime(2000, 1, 1))
        ddb.gui.setvar(group, "tstop", datetime.datetime(2000, 1, 3))

        ddb.gui.setvar(group, "roughness_type", "landsea")

        # Now set some extra variables needed for SFINCS GUI
        ddb.gui.setvar(group, "input_options_text", ["Binary", "ASCII"])
        ddb.gui.setvar(group, "input_options_values", ["bin", "asc"])

        ddb.gui.setvar(group, "output_options_text", ["NetCDF", "Binary", "ASCII"])
        ddb.gui.setvar(group, "output_options_values", ["net", "bin", "asc"])

    def set_model_variables(self, varid=None, value=None):

        group = "sfincs"

        for var_name in self.domain.config:
            self.domain.config[var_name] = ddb.gui.variables[group][var_name]["value"]
#            setattr(self.domain.input, var_name, ddb.gui.variables[group][var_name]["value"])

    def initialize_domain(self):

        self.domain = SfincsModel()

    def set_input_variable(self, gui_variable, value):

        pass

