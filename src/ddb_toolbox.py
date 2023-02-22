# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb

class GenericToolbox:
    def __init__(self):
        pass

    def select(self):

        ddb.active_toolbox = self
        ddb.gui.setvar("menu", "active_toolbox_name", ddb.active_toolbox.name)

        # Get index of active model
        index = list(ddb.model).index(ddb.active_model.name)

        # Toolbox tab
        tab = ddb.gui.window.elements[index].tabs[0]
        tab.widget.parent().parent().setTabText(0, ddb.active_toolbox.long_name)

        # First remove old toolbox elements from first tab
        tab.elements = []
        ddb.gui.window.elements[index].clear_tab(0)

        # Now add toolbox elements to first tab
        ddb.gui.window.add_elements_to_tree(tab.elements, self.element, tab, ddb.gui, ddb.gui.window)
        ddb.gui.window.add_elements(tab.elements)

        ddb.gui.window.update()

    def add_layers(self):
        pass


def select_toolbox(toolbox_name):
    # Called from menu, or from ddb_model->select
    ddb.active_toolbox = ddb.toolbox[toolbox_name]
    ddb.active_toolbox.select()
    # # And go to this tab
    # ddb.gui.window.elements[0].widget.select_tab(0)
    # ddb.gui.update()

