# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: ormondt
"""

__version__ = "0.0.1"

from delftdashboard.app import app    

def start():
    print("Starting Delft Dashboard")    
    # Initialize
    app.initialize()
    # Build the GUI
    app.gui.build()
