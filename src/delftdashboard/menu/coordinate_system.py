# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

from delftdashboard.app import app
from pyproj import CRS

def wgs84(option):
    new_crs = CRS(4326)
    if new_crs == app.crs:
        return    
    app.crs = new_crs
    app.map.fly_to(0.0, 0.0, 1)
    update_crs()

def other_geographic(option):
    print("Other")

def utm_zone(option):
    okay, data = app.gui.popup(os.path.join(app.main_path, "misc", "select_utm_zone","utm_zone.yml"), None)
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
    new_crs = CRS("WGS 84 / UTM zone " + utm)
    if new_crs == app.crs:
        return    
    app.crs = new_crs
    app.map.fly_to(lon, lat, zoom)
    update_crs()


def other_projected(option):
    print("Other")

def update_crs():
    app.map.crs = app.crs
    # Also change the model crs
    for model in app.model:
        try:
            app.model[model].set_crs()
        except:
            print("No method set_crs for model: ", model)
    # Also change the toolbox crs
    for toolbox in app.toolbox:
        app.toolbox[toolbox].set_crs()
    app.gui.window.update()    

