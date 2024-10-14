# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

class DelftDashboard:
    def __init__(self):
        pass

    def initialize(self):
        from .operations import initialize
        self.main_path = os.path.dirname(os.path.abspath(__file__))
        print(self.main_path)
        initialize.initialize()

app = DelftDashboard()
