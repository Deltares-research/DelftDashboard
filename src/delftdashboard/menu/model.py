# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations.model import select_model

def select(model_name):
    select_model(model_name)
