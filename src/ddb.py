# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os
import time
import sched




class DelftDashboard:
    def __init__(self):
        pass

    def initialize(self):
        import ddb_initialize
        ddb_initialize.initialize()

    def update_map(self):
        import ddb_map
        ddb_map.update()


    def on_build(self):
        # Called from GUI model after the GUI has built
#        self.on_map_ready()
        pass
#        self.check_map_ready()

    # def on_map_ready(self):
    #     # Called when map is ready
    #
    #     # Add layers to map
    #     for name, toolbox in ddb.toolbox.items():
    #         toolbox.add_layers()
    #
    #     # Default model is first model in config
    #     model_name = list(ddb.model.keys())[0]
    #     # Select this model (this will update the menu and add the toolbox)
    #     ddb.model[model_name].select()

    # def check_map_ready(self):
    #     # Check if map is ready
    #     # If not, try again in 1 second
    #     print(self.gui.map_widget["map"].ready)
    #     if self.gui.map_widget["map"].ready:
    #         self.on_map_ready()
    #     else:
    #         s = sched.scheduler(time.time, time.sleep)
    #         s.enter(1.0, 1, self.check_map_ready)
    #         s.run()



ddb = DelftDashboard()
