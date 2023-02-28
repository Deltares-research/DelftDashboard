# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb

def globe(option):
    if ddb.view["projection"] != "globe":
        ddb.view["projection"] = "globe"
        ddb.gui.setvar("menu", "projection", "globe")
        ddb.map.set_projection("globe")
        ddb.gui.window.update()

def mercator(option):
    if ddb.view["projection"] != "mercator":
        ddb.view["projection"] = "mercator"
        ddb.gui.setvar("menu", "projection", "mercator")
        ddb.map.set_projection("mercator")
        ddb.gui.window.update()

def topography(option):
    if ddb.view["topography"]["visible"] == False:
        ddb.view["topography"]["visible"] = True
        ddb.gui.setvar("menu", "show_topography", True)
    else:
        ddb.view["topography"]["visible"] = False
        ddb.gui.setvar("menu", "show_topography", False)
    ddb.map.layer["main"].layer["background_topography"].set_visibility(ddb.view["topography"]["visible"])
    ddb.gui.window.update()


def layer_style(option):
    ddb.gui.setvar("menu", "layer_style", option)
    if ddb.view["layer_style"] == option:
        pass
    else:
        ddb.map.set_layer_style(option)
    ddb.view["layer_style"] = option
    ddb.gui.window.update()

def terrain(option):
    if ddb.view["terrain"]["visible"] == False:
        ddb.view["terrain"]["visible"] = True
        ddb.gui.setvar("menu", "show_terrain", True)
    else:
        ddb.view["terrain"]["visible"] = False
        ddb.gui.setvar("menu", "show_terrain", False)
    ddb.map.set_terrain(ddb.view["terrain"]["visible"], ddb.view["terrain"]["exaggeration"])
