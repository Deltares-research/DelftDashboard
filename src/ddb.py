# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

class DelftDashboard:
    def __init__(self):
        pass

    def initialize(self):
        import ddb_initialize
        ddb_initialize.initialize()

    def on_build(self):
        # Default model is first model in config
        model_name = list(ddb.model.keys())[0]
        # Select this model
        # This will update the menu and add the toolbox
        ddb.model[model_name].select()

ddb = DelftDashboard()
