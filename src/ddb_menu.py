# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb

def new(id, option):
    print(id)
    print(option)

def open(option):
    ddb.active_model.open()

def save(option):
    ddb.active_model.save()
