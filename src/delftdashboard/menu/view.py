# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app


def globe(option):
    if app.view["projection"] != "globe":
        app.view["projection"] = "globe"
        app.gui.setvar("menu", "projection", "globe")
        app.map.set_projection("globe")
        app.gui.window.update()


def mercator(option):
    if app.view["projection"] != "mercator":
        app.view["projection"] = "mercator"
        app.gui.setvar("menu", "projection", "mercator")
        app.map.set_projection("mercator")
        app.gui.window.update()


def topography(option):
    if app.view["topography"]["visible"] == False:
        app.view["topography"]["visible"] = True
        app.gui.setvar("menu", "show_topography", True)
    else:
        app.view["topography"]["visible"] = False
        app.gui.setvar("menu", "show_topography", False)
    app.map.layer["main"].layer["background_topography"].set_visibility(
        app.view["topography"]["visible"]
    )
    app.gui.window.update()


def layer_style(option):
    app.gui.setvar("menu", "layer_style", option)
    if app.view["layer_style"] != option:
        app.map.set_layer_style(option)
    app.view["layer_style"] = option
    # # No redraw all layers
    # app.map.redraw_layers()
    app.gui.window.update()


def terrain(option):
    if app.view["terrain"]["visible"] == False:
        app.view["terrain"]["visible"] = True
        app.gui.setvar("menu", "show_terrain", True)
    else:
        app.view["terrain"]["visible"] = False
        app.gui.setvar("menu", "show_terrain", False)
    app.map.set_terrain(
        app.view["terrain"]["visible"], app.view["terrain"]["exaggeration"]
    )
