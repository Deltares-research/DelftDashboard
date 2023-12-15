# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()

def set_variables(*args):
    app.active_model.set_input_variables()

def select_occupancy_type(*args):
    print("Select occupancy type")

def filter_damage_curve_table(*args):
    selected_occupancy_type = app.gui.getvar("fiat", "selected_occupancy_type")
    df = app.active_model.get_filtered_damage_function_database(selected_occupancy_type)
    app.gui.setvar("fiat", "damage_curves_standard_info", df)
