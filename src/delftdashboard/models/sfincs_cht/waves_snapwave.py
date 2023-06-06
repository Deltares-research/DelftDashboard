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


def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()


def draw_boundary_enclosure(*args):
    app.map.layer["sfincs_cht"].layer["snapwave_boundary_enclosure"].draw()


def boundary_enclosure_created(gdf, index, id):
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.gdf = gdf
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.write()
    app.model["sfincs_cht"].domain.input.variables.snapwave_encfile = "snapwave.enc"
    # 
    app.model["sfincs_cht"].domain.input.variables.snapwave_bndfile = "snapwave.bnd"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bhsfile = "snapwave.bhs"
    app.model["sfincs_cht"].domain.input.variables.snapwave_btpfile = "snapwave.btp"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bwdfile = "snapwave.bwd"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bdsfile = "snapwave.bds"
    app.model["sfincs_cht"].domain.snapwave.boundary_conditions.add_point(1.5, 2.5, hs=5.0, tp=12.0, wd=180.0, ds=30.0)
    app.model["sfincs_cht"].domain.snapwave.boundary_conditions.write()


def boundary_enclosure_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.gdf = gdf
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.write()
    app.model["sfincs_cht"].domain.input.variables.snapwave_encfile = "snapwave.enc"
