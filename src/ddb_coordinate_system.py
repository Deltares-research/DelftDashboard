# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from ddb import ddb
from pyproj import CRS

def wgs84(option):
    print("WGS 84")

def other_geographic(option):
    print("Other")

def utm_zone(option):
    data = ddb.gui.popup("c:\\work\checkouts\\git\\DelftDashboard\\src\\toolboxes\\modelmaker_sfincs\\popuptest\\utm_zone.yml", None, modal=True)
    if not data:
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
    ddb.gui.map_widget["map"].fly_to(lon, lat, zoom)

def other_projected(option):
    print("Other")
