# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb
from guitares.gui import add_elements

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

        #

#        tab = ddb.active_model_panel["tab"][0]["widget"]
        # Get index of active model
        model = ddb.active_model.name
#        models = list(ddb.model)
        index = list(ddb.model).index(model)

        # Toolbox tab
        tab = ddb.gui.config["element"][index]["tab"][0]

        # First remove old toolbox elements from first tab
        for child in tab["widget"].children():
            child.setParent(None)

        # Now add toolbox elements to first tab
        tab["element"] = self.element
        add_elements(self.element, tab["widget"], ddb.gui)

        ddb.active_toolbox = self

    def add_layers(self):
        pass


def select_toolbox(toolbox_name):
    # Called from menu, or from ddb_model->select
    ddb.toolbox[toolbox_name].select()
    # And go to this tab
    ddb.gui.config["element"][0]["widget"].select_tab(0)
    ddb.gui.update()

