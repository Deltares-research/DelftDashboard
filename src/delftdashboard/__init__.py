# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 10:58:08 2021

@author: ormondt
"""

from delftdashboard.app import app    

def start():
    print("Starting Delft Dashboard")    
    # Initialize
    app.initialize()
    # Build the GUI
    app.gui.build()
