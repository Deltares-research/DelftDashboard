# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 10:08:26 2021

@author: ormondt
"""

import pandas as pd
import numpy as np

def read_colormap(file_name):
    
    df = pd.read_csv(file_name, index_col=False, header=None,
                  delim_whitespace=True, names=['r','g','b'])
    v = df.to_numpy()

    return v
     