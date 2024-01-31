# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app
import inspect


class GenericToolbox:
    def __init__(self):
        pass

    def select(self):

        app.active_toolbox = self
        app.gui.setvar("menu", "active_toolbox_name", app.active_toolbox.name)

        # Get index of active model
        index = list(app.model).index(app.active_model.name)

        # Toolbox tab
        tab = app.gui.window.elements[index].tabs[0]
        tab.module = app.active_toolbox.module
        tab.widget.parent().parent().setTabText(0, app.active_toolbox.long_name)

        # First remove old toolbox elements from first tab
        app.gui.window.elements[index].clear_tab(0)

        # Now add toolbox elements to first tab
        app.gui.window.add_elements_to_tree(self.element, tab, app.gui.window)
        app.gui.window.add_elements(tab.elements)

        # And select this tab
        app.gui.window.elements[index].widget.select_tab(0)

        app.gui.window.update()

    def add_layers(self):
        pass

    def set_crs(self):
        pass


def select_toolbox(toolbox_name):
    # Called from menu, or from model->select
    app.active_toolbox = app.toolbox[toolbox_name]
    app.active_toolbox.select()
    # # And go to this tab
    # app.gui.window.elements[0].widget.select_tab(0)
    # app.gui.window.update()
