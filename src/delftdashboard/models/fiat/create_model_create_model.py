# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map
from pathlib import Path
import yaml
import copy


def select(*args):
    # De-activate existing layers
    map.update()

def create_model(*args):
    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        return
    
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

    dlg.close()
    app.gui.window.dialog_info(
            f"A FIAT model is created in:\n{app.active_model.domain.fiat_model.root}",
            "FIAT model created",
        )

# This function is not functional and is just a test.
def update_damage_values():
        
        # Open Strucutre file
        max_damage_struct_fn = Path(app.active_model.domain.fiat_model.root) / "structure_update_damage.yaml"
        if max_damage_struct_fn.exists():
            with open(max_damage_struct_fn, 'r') as yaml_file:
                    updated_damages_struct = yaml.safe_load(yaml_file)

            app.active_model.domain.exposure_vm.exposure.setup_max_potential_damage(
                max_potential_damage=updated_damages_struct["source"],
                damage_types=updated_damages_struct["damage_types"],    
                attr_name=updated_damages_struct["attribute_name"],
                method=updated_damages_struct["method"],
                max_dist=updated_damages_struct["max_dist"]
            )
            # Rewrite the model with new input
            app.active_model.domain.fiat_model.write()

        # Open content file
        max_damage_cont_fn = Path(app.active_model.domain.fiat_model.root) / "content_update_damage.yaml"        
        if max_damage_cont_fn.exists():
            with open(max_damage_cont_fn, 'r') as yaml_file:
                    updated_damages_cont = yaml.safe_load(yaml_file)

            app.active_model.domain.exposure_vm.exposure.setup_max_potential_damage(
                    max_potential_damage=updated_damages_cont["source"],
                    damage_types=updated_damages_cont["damage_types"],    
                    attr_name=updated_damages_cont["attribute_name"],
                    method=updated_damages_cont["method"],
                    max_dist=updated_damages_cont["max_dist"]
                )
                # Rewrite the model with new input 
            app.active_model.domain.fiat_model.write()

        config = app.active_model.domain.build_config_yaml()
        config.setup_exposure_buildings
        # Return updated buildings and roads
        '''exposure_db = app.active_model.domain.exposure_vm.exposure.exposure_db
        if (
            app.active_model.domain.exposure_vm.exposure_buildings_model != None
            and app.active_model.domain.exposure_vm.exposure_roads_model == None
        ):
            # Only buildings are set up
            buildings_gdf = app.active_model.domain.fiat_model.exposure.get_full_gdf(exposure_db)
            return buildings_gdf, None
        elif (
            app.active_model.domain.exposure_vm.exposure_buildings_model != None
            and app.active_model.domain.exposure_vm.exposure_roads_model != None
        ):
            # Buildings and roads are set up
            full_gdf = app.active_model.domain.fiat_model.exposure.get_full_gdf(exposure_db)
            buildings_gdf = full_gdf.loc[full_gdf["Primary Object Type"] != "roads"]
            roads_gdf = full_gdf.drop(["SVI", "SVI_key_domain"], axis=1).loc[
                full_gdf["Primary Object Type"] == "roads"
            ]
            return buildings_gdf, roads_gdf
        elif (
            app.active_model.domain.exposure_vm.exposure_buildings_model == None
            and app.active_model.domain.exposure_vm.exposure_roads_model != None
        ):
            # Only roads are set up
            roads_gdf = app.active_model.domain.fiat_model.exposure.get_full_gdf(exposure_db).drop(
                ["SVI", "SVI_key_domain"], axis=1
            )
            return None, roads_gdf '''
    

def edit(*args):
    app.active_model.set_model_variables()
