# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb
from guitools.gui import add_elements

class GenericToolbox:
    def __init__(self):
        pass

    def select(self):

        # Set this toolbox checked (and the other ones unchecked)
        for menu in ddb.gui.config["menu"]:
            if menu["text"] == "Toolbox":
                for m in menu["menu"]:
                    if m["id"] == self.name:
                        m["widget"].setChecked(True)
                    else:
                        m["widget"].setChecked(False)

        # First remove old toolbox elements from first tab
        tab = ddb.active_model_panel["tab"][0]["widget"]
        for child in tab.children():
            child.setParent(None)

        # Now add toolbox elements to first tab
        ddb.active_model_panel["tab"][0]["element"] = self.element
        tab_widget = ddb.active_model_panel["tab"][0]["widget"]
        add_elements(self.element, tab_widget, ddb.gui.main_window, ddb.gui.server_path, ddb.gui.server_port)

        ddb.active_toolbox = self

    def add_layers(self):
        pass


def select_toolbox(toolbox_name):
    # Called from menu, or from ddb_model->select
    ddb.toolbox[toolbox_name].select()
    # And go to this tab
    ddb.gui.config["element"][0]["select_tab"](0)
