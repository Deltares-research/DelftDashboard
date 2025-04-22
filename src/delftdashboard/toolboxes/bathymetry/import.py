# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import xarray as xr

from delftdashboard.app import app
from delftdashboard.operations import map

# Callbacks

def select(*args):
    # Tab selected
    # De-activate() existing layers
    map.update()

def select_import_file_format(*args):
    fmt = app.gui.getvar("bathymetry", "import_file_format")
    if fmt == "geotiff":
        app.gui.setvar("bathymetry", "import_file_filter", "GeoTIFF (*.tif;*.tiff)")
    elif fmt == "netcdf":
        app.gui.setvar("bathymetry", "import_file_filter", "NetCDF (*.nc)")
    elif fmt == "xyz":
        app.gui.setvar("bathymetry", "import_file_filter", "XYZ (*.xyz)")
    else:
        app.gui.setvar("bathymetry", "import_file_filter", "")

def select_import_file(*args):
    app.gui.setvar("bathymetry", "import_file_selected", True)
    # Get the file name without path and extension
    filename = app.gui.getvar("bathymetry", "import_file_name")
    basename = os.path.basename(filename)
    name, ext = os.path.splitext(basename)
    # Set the dataset name to the file name without path and extension
    app.gui.setvar("bathymetry", "dataset_name", name)    
    app.gui.setvar("bathymetry", "dataset_long_name", name)

    fmt = app.gui.getvar("bathymetry", "import_file_format")
    if fmt == "netcdf":
        # Need to get a list with the variable names
        # Use xarray to open the netcdf file and get the variable names
        wb = app.gui.window.dialog_wait("Loading dataset ...")
        ds = xr.open_dataset(filename)
        variable_names = list(ds.data_vars)
        # Remove variables that are not 2D
        variable_names = [name for name in variable_names if ds[name].ndim == 2]        
        ds.close()
        # Set the dataset name to the first variable name
        app.gui.setvar("bathymetry", "variable_names", variable_names)
        app.gui.setvar("bathymetry", "variable_name", variable_names[0])
        wb.close()

def edit_dataset_name(*args):
    pass

def edit_dataset_long_name(*args):
    pass

def edit_dataset_source(*args):
    pass

def select_variable_name(*args):
    pass

def select_import_as(*args):
    pass

def import_dataset(*args):
    app.toolbox["bathymetry"].import_dataset()
