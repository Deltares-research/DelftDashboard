# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

from ddb import ddb
from pyproj import CRS

def wgs84(option):
    print("WGS 84")

def other_geographic(option):
    print("Other")

def utm_zone(option):
    okay, data = ddb.gui.popup(os.path.join(ddb.main_path, "misc", "select_utm_zone","utm_zone.yml"), None)
    if not okay:
        return
    letters = ['C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']
    utm = data["utm_zone"]
    utm_letter = data["utm_letter"]
    utm_number = int(utm[0:-1])
    index = letters.index(utm_letter) + 1
    lon = -180.0 + utm_number*6.0 - 3.0
    lat = -80.0 + index*8.0 - 4.0
    zoom = 6
    ddb.crs = CRS("WGS 84 / UTM zone " + utm)
    # Also change the model crs
    for model in ddb.model:
        ddb.model[model].set_crs(ddb.crs)
    ddb.map.fly_to(lon, lat, zoom)

def other_projected(option):
    print("Other")
