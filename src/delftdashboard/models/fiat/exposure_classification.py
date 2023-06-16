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


def select_selected_primary_classification(*args):
    print("Select primary classification type")


def move_up_selected_primary_classification(*args):
    print("Move up primary classification field")


def move_down_selected_primary_classification(*args):
    print("Move down primary classification field")


def remove_selected_primary_classification(*args):
    print("Remove primary classification field")


def select_selected_secondary_classification(*args):
    print("Select secondary classification type")


def move_up_selected_secondary_classification(*args):
    print("Move up primary classification field")


def move_down_selected_secondary_classification(*args):
    print("Move down primary classification field")


def remove_selected_secondary_classification(*args):
    print("Remove primary classification field")


def display_primary_classification(*args):
    print("Display primary classification fields")


def display_secondary_classification(*args):
    print("Display secondary classification fields")