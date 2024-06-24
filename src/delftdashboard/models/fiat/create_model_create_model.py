# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
import geopandas as gpd
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    if all(values.data is None for key, values in app.map.layer["buildings"].layer.items()):
        app.map.layer["modelmaker_fiat"].layer[app.gui.getvar("modelmaker_fiat", "active_area_of_interest")].show()
    app.gui.setvar("_main", "show_fiat_checkbox", True)


def create_model(*args):
    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        return

    # If model was already created create pop-up to ask if should be overwritten?
    if app.active_model.domain.fiat_model.exposure is not None:
        try:
            app.active_model.overwrite_model()
        except ValueError as e:
            return  
        app.map.layer["buildings"].clear()

    dlg = app.gui.window.dialog_wait("\nCreating a FIAT model...")

    try:
        buildings, roads = app.active_model.domain.run_hydromt_fiat()
    except Exception as e:
        app.gui.window.dialog_warning(
            str(e),
            "Not ready to build a FIAT model",
        )
        dlg.close()
        return

    if buildings is not None:
        app.active_model.buildings = buildings
    if roads is not None:
        app.active_model.roads = roads

    # Set the unit for Exposure Data for visualization
    view_tab_unit = app.active_model.domain.fiat_model.exposure.unit
    app.gui.setvar("fiat", "view_tab_unit", view_tab_unit)

    # Show exposure buildings
    display_asset_locations()

    dlg.close()
        
    app.gui.window.dialog_info(
        f"A FIAT model is created in:\n{app.active_model.domain.fiat_model.root}",
        "FIAT model created",
    )


def edit(*args):
    app.active_model.set_model_variables()

def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.map.layer["buildings"].layer["exposure_points"].crs = crs = app.gui.getvar(
        "fiat", "selected_crs"
    )

    if not app.gui.getvar("fiat", "bf_conversion"):
        point_buildings = app.active_model.convert_bf_into_centroids(app.active_model.buildings, app.gui.getvar(
        "fiat", "selected_crs"
        ))
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            point_buildings
        )
        app.active_model.buildings = point_buildings
    else:
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            app.active_model.buildings
        )
    app.active_model.show_exposure_buildings()

