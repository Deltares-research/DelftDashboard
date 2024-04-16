# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

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
    app.map.layer["main"].layer["background_topography"].set_visibility(app.view["topography"]["visible"])
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
    app.map.set_terrain(app.view["terrain"]["visible"], app.view["terrain"]["exaggeration"])

def settings(option):

    # A lot of copying here. Should we just use setvar and getvar for the settings ? No, because we want to be able to cancel the settings.
    app.gui.setvar("topography_view_settings", "colormap", app.view["topography"]["colormap"])
    app.gui.setvar("topography_view_settings", "autoscaling", app.view["topography"]["autoscaling"])
    app.gui.setvar("topography_view_settings", "zmin", app.view["topography"]["zmin"])
    app.gui.setvar("topography_view_settings", "zmax", app.view["topography"]["zmax"])
    app.gui.setvar("topography_view_settings", "opacity", app.view["topography"]["opacity"])

    # Open settings window
    okay, data = app.gui.popup(os.path.join(app.main_path, "misc", "view_settings","view_settings.yml"), id="view_settings")
    if not okay:
        return

    # Okay was pressed, so update view settings
    app.view["topography"]["colormap"] = app.gui.getvar("topography_view_settings", "colormap")
    app.view["topography"]["autoscaling"] = app.gui.getvar("topography_view_settings", "autoscaling")
    app.view["topography"]["zmin"] = app.gui.getvar("topography_view_settings", "zmin")
    app.view["topography"]["zmax"] = app.gui.getvar("topography_view_settings", "zmax")
    app.view["topography"]["opacity"]  = app.gui.getvar("topography_view_settings", "opacity")

    # Updata topography layer
    app.background_topography_layer.color_map = app.view["topography"]["colormap"]
    app.background_topography_layer.color_scale_auto = app.view["topography"]["autoscaling"]
    app.background_topography_layer.color_scale_cmin = app.view["topography"]["zmin"]
    app.background_topography_layer.color_scale_cmax = app.view["topography"]["zmax"]
    # app.background_topography_layer.color_scale_symmetric = app.view["topography"]["color_scale_symmetric"]
    app.background_topography_layer.opacity = app.view["topography"]["opacity"]

    # # Update view
    # app.view["terrain"]["exaggeration"] = data["terrain_exaggeration"]
    # app.view["terrain"]["visible"] = data["show_terrain"]
    # app.view["topography"]["visible"] = data["show_topography"]
    # app.view["layer_style"] = data["layer_style"]
    # # Update GUI
