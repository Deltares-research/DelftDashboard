# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb

def globe(option):
    if ddb.view["projection"] == "globe":
        # Do nothing
        pass
    else:
        item = ddb.gui.find_menu_item_by_id(ddb.gui.config["menu"], "view.globe")
        item["widget"].setChecked(True)
        item = ddb.gui.find_menu_item_by_id(ddb.gui.config["menu"], "view.mercator")
        item["widget"].setChecked(False)
        ddb.view["projection"] = "globe"
        ddb.map.set_projection("globe")

def mercator(option):
    if ddb.view["projection"] == "mercator":
        # Do nothing
        pass
    else:
        item = find_menu_item_by_id(ddb.gui.config["menu"], "view.globe")
        item["widget"].setChecked(False)
        item = find_menu_item_by_id(ddb.gui.config["menu"], "view.mercator")
        item["widget"].setChecked(True)
        ddb.view["projection"] = "mercator"
        ddb.map.set_projection("mercator")

def topography(option):
    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.topography")
    if ddb.view["topography"]["visible"]:
        item["widget"].setChecked(False)
        ddb.view["topography"]["visible"] = False
    else:
        item["widget"].setChecked(True)
        ddb.view["topography"]["visible"] = True
    ddb.map.layer["main"].layer["background_topography"].set_visibility(ddb.view["topography"]["visible"])

def layer_style(option):
    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.layer_style.streets")
    if option == "streets":
        item["widget"].setChecked(True)
    else:
        item["widget"].setChecked(False)

    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.layer_style.satellite")
    if option == "satellite":
        item["widget"].setChecked(True)
    else:
        item["widget"].setChecked(False)

    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.layer_style.satellite_streets")
    if option == "satellite_streets":
        item["widget"].setChecked(True)
    else:
        item["widget"].setChecked(False)

    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.layer_style.light")
    if option == "light":
        item["widget"].setChecked(True)
    else:
        item["widget"].setChecked(False)

    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.layer_style.dark")
    if option == "dark":
        item["widget"].setChecked(True)
    else:
        item["widget"].setChecked(False)

    if ddb.view["layer_style"] == option:
        pass
    else:
        ddb.map.set_layer_style(option)

    ddb.view["layer_style"] = option

def terrain(option):
    item = find_menu_item_by_id(ddb.gui.config["menu"], "view.terrain")
    if ddb.view["terrain"]["visible"]:
        item["widget"].setChecked(False)
        ddb.view["terrain"]["visible"] = False
    else:
        item["widget"].setChecked(True)
        ddb.view["terrain"]["visible"] = True
    ddb.map.set_terrain(ddb.view["terrain"]["visible"], ddb.view["terrain"]["exaggeration"])
