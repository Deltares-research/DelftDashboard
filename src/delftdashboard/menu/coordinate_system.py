# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

import os

from delftdashboard.app import app
from delftdashboard.operations import map

import pyproj
from pyproj import CRS


def wgs84(option):
    new_crs = CRS(4326)
    if new_crs == app.crs:
        return
    app.crs = new_crs
    app.map.fly_to(0.0, 0.0, 1)
    update_crs()


def utm_zone(option):
    okay, data = app.gui.popup(
        os.path.join(app.main_path, "misc", "select_utm_zone", "utm_zone.yml"),
        id="utm_zone",
        data=None,
    )
    if not okay:
        return
    letters = [
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "J",
        "K",
        "L",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
    ]
    utm = data["utm_zone"]
    utm_letter = data["utm_letter"]
    utm_number = int(utm[0:-1])
    index = letters.index(utm_letter) + 1
    lon = -180.0 + utm_number * 6.0 - 3.0
    lat = -80.0 + index * 8.0 - 4.0
    zoom = 6
    new_crs = CRS("WGS 84 / UTM zone " + utm)
    if new_crs == app.crs:
        return
    app.crs = new_crs
    app.map.fly_to(lon, lat, zoom)
    update_crs()


def other_projected(option):

    # Get a list of all CRS
    crs_info_list = pyproj.database.query_crs_info(auth_name=None, pj_types=None)

    crs_names = []
    for crs_info in crs_info_list:
        # Check if the CRS is a projected CRS
        if crs_info.type.name.lower() == "projected_crs":
            crs_names.append(crs_info.name)

    data = {}
    data["crs_info_list"] = crs_info_list
    app.gui.setvar("select_other_projected", "crs_names", crs_names)
    app.gui.setvar("select_other_projected", "filtered_names", crs_names)
    app.gui.setvar("select_other_projected", "search_string", "")
    app.gui.setvar("select_other_projected", "crs_index", 0)

    okay, data = app.gui.popup(
        os.path.join(app.main_path, "misc", "select_other_projected", "select_other_projected.yml"),
        id="select_other_projected",
        data=data,
    )

    if not okay:
        return

    filtered_names = app.gui.getvar("select_other_projected", "filtered_names")
    i = app.gui.getvar("select_other_projected", "crs_index")
    selected_name = filtered_names[i]
    
    new_crs = CRS(selected_name)

    if new_crs == app.crs:
        return

    app.crs = new_crs

    if new_crs.area_of_use:
        lon = (new_crs.area_of_use.west + new_crs.area_of_use.east) / 2
        lat = (new_crs.area_of_use.south + new_crs.area_of_use.north) / 2
        zoom = 4
    app.map.fly_to(lon, lat, zoom)

    app.gui.delgroup("select_other_projected")

    update_crs()

def other_geographic(option):

    # Get a list of all CRS
    crs_info_list = pyproj.database.query_crs_info(auth_name=None, pj_types=None)

    crs_names = []
    for crs_info in crs_info_list:
        # Check if the CRS is a geographic CRS
        if crs_info.type.name.lower() == "geographic_2d_crs":
            crs_names.append(crs_info.name)

    data = {}
    data["crs_info_list"] = crs_info_list
    app.gui.setvar("select_other_geographic", "crs_names", crs_names)
    app.gui.setvar("select_other_geographic", "filtered_names", crs_names)
    app.gui.setvar("select_other_geographic", "search_string", "")
    app.gui.setvar("select_other_geographic", "crs_index", 0)

    okay, data = app.gui.popup(
        os.path.join(app.main_path, "misc", "select_other_geographic", "select_other_geographic.yml"),
        id="select_other_geographic",
        data=data,
    )

    if not okay:
        return

    filtered_names = app.gui.getvar("select_other_geographic", "filtered_names")
    i = app.gui.getvar("select_other_geographic", "crs_index")
    selected_name = filtered_names[i]
    
    new_crs = CRS(selected_name)

    if new_crs == app.crs:
        return

    app.crs = new_crs

    app.gui.delgroup("select_other_geographic")

    update_crs()

def update_crs():
    app.map.crs = app.crs
    # Also change the model crs
    for model in app.model:
        app.model[model].set_crs()
    # Also change the toolbox crs
    for toolbox in app.toolbox:
        app.toolbox[toolbox].set_crs()
    app.gui.window.update()
    map.update_statusbar()  # Update crs in statusbar
