# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from ddb_models import models
from ddb_gui import gui


def select():
    gui.main_window.update_active_tab()


def set_variables():
    # All variables will be set
    models.model["sfincs"].set_model_variables()
    gui.main_window.update_active_tab()
