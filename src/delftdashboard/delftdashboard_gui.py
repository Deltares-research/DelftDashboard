# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app
import pooch

if __name__ == '__main__':

    # Initialize
    app.initialize()

    # Build the GUI
    app.gui.build()
