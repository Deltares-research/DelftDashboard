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


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def add_classification_field(*args):
    print("Add classification field")


def load_nsi_classification_source(*args):
    print("Load NSI classification source")


def load_loaded_classification_source(*args):
    print("Load loaded classification source")


def display_primary_classification(*args):
    print("Display primary classification fields")


def display_secondary_classification(*args):
    print("Display secondary classification fields")


def standarize_classification(*args):
    app.model["fiat"].classification_standarize()


def add_classification(*args):
    print("Add classification to model")