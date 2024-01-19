# -*- coding: utf-8 -*-
from delftdashboard.app import app
import pooch

if __name__ == "__main__":
    # Initialize
    app.initialize()

    # Build the GUI
    app.gui.build()
