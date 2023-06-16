# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()

def edit(*args):
    app.model["fiat"].set_model_variables()


def select_selected_primary_classification(*args):
    print("Select primary classification type")


def select_selected_secondary_classification(*args):
    print("Select secondary classification type")


def display_primary_classification(*args):
    print("Display primary classification fields")


def display_secondary_classification(*args):
    print("Display secondary classification fields")