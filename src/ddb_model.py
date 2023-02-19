# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import importlib

from ddb import ddb
from ddb_toolbox import select_toolbox
from guitares.gui import set_missing_menu_values

class GenericModel:
    def __init__(self):
        self.name      = "model"
        self.long_name = "Model"
        self.exe_path  = None

    def open(self):
        pass

    def add_layers(self):
        pass

    def select(self):

        elements = ddb.gui.config["element"]

        # Set all tab panel for current model to visible
        for element in elements:
            if element["style"] == "tabpanel":
                if element["id"] == self.name:
                    element["widget"].setVisible(True)
                    element["visible"] = True
#                    ddb.active_model_panel = element
        # And the others to invisible
        for element in elements:
            if element["style"] == "tabpanel":
                if element["id"] != self.name:
                    element["widget"].setVisible(False)
                    element["visible"] = False

        ddb.active_model = self

        # Set this model checked in the menu (and the other ones unchecked)
        for menu in ddb.gui.config["menu"]:
            if menu["text"] == "Model":
                for m in menu["menu"]:
                    if m["id"] == self.name:
                        m["widget"].setChecked(True)
                    else:
                        m["widget"].setChecked(False)


        # Check which toolboxes we can add and update the menu
        toolboxes_to_add = []
        for toolbox_name in ddb.toolbox:
            if toolbox_name in self.toolbox:
                toolboxes_to_add.append(toolbox_name)

        # Clear toolbox menu
        toolbox_menu = ddb.gui.config["menu"][2]
        toolbox_menu["widget"].clear()

        # Add toolboxes_to_add
        menu_to_add = []
        for toolbox_name in toolboxes_to_add:
            menu_to_add.append({"text": ddb.toolbox[toolbox_name].long_name,
                                "module": "ddb_toolbox",
                                "method": "select_toolbox",
                                "id": toolbox_name,
                                "option": toolbox_name,
                                "checkable": True})
        set_missing_menu_values(menu_to_add, "ddb_toolbox")
        toolbox_menu["menu"] = menu_to_add
        ddb.gui.menu.add_menu(menu_to_add, toolbox_menu["widget"])


        # Check if the current toolbox is available. If not, select a new toolbox.
        if ddb.active_toolbox.name in toolboxes_to_add:
            # Select active toolbox
            select_toolbox(ddb.active_toolbox.name)
        else:
            # Select first toolbox from the list
            select_toolbox(toolboxes_to_add[0])

def select_model(model_name):
    # Called from menu
    ddb.model[model_name].select()
