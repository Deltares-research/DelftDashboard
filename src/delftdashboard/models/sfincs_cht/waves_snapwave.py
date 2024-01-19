# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate() existing layers
    map.update()
    app.map.layer["sfincs_cht"].layer["snapwave_boundary_enclosure"].activate()


def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_cht"].set_model_variables()


def draw_boundary_enclosure(*args):
    app.map.layer["sfincs_cht"].layer["snapwave_boundary_enclosure"].draw()


def boundary_enclosure_created(gdf, index, id):
    # Check if this is a new enclosure
    if len(gdf)>1:
        gdf = gpd.GeoDataFrame(geometry=[gdf.loc[1]["geometry"]], crs=gdf.crs)
    app.map.layer["sfincs_cht"].layer["snapwave_boundary_enclosure"].set_data(gdf)    
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.gdf = gdf
    app.model["sfincs_cht"].domain.input.variables.snapwave_encfile = "snapwave.enc"
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.write()
    # Boundary conditions (should do this somewhere else) 
    app.model["sfincs_cht"].domain.input.variables.snapwave_bndfile = "snapwave.bnd"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bhsfile = "snapwave.bhs"
    app.model["sfincs_cht"].domain.input.variables.snapwave_btpfile = "snapwave.btp"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bwdfile = "snapwave.bwd"
    app.model["sfincs_cht"].domain.input.variables.snapwave_bdsfile = "snapwave.bds"
    app.model["sfincs_cht"].domain.snapwave.boundary_conditions.add_point(0.0, 0.0, hs=5.0, tp=12.0, wd=180.0, ds=30.0)
    app.model["sfincs_cht"].domain.snapwave.boundary_conditions.write()


def boundary_enclosure_modified(gdf, index, id):
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.gdf = gdf
    app.model["sfincs_cht"].domain.snapwave.boundary_enclosure.write()
    app.model["sfincs_cht"].domain.input.variables.snapwave_encfile = "snapwave.enc"
