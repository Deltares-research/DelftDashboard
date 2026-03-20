# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

def select(*args):
    # De-activate existing layers
    map.update()
    # Activate draw layer
    app.map.layer["sfincs_hmt"].layer["drainage_structures"].activate()
    update()

def deselect(*args):
    if app.model["sfincs_hmt"].drainage_structures_changed:
        if app.model["sfincs_hmt"].domain.drainage_structures.nr_lines == 0:
            # No drainage_structures, so just reset the flag and return
            app.model["sfincs_hmt"].drainage_structures_changed = False
            return
        ok = app.gui.window.dialog_yes_no("The drainage_structures have changed. Would you like to save the changes?")
        if ok:
            save()

def load(*args):
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          file_name="sfincs.drn",
                                          filter="*.drn",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("drnfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.drainage_structures.read()
        gdf = app.model["sfincs_hmt"].domain.drainage_structures.gdf
        app.map.layer["sfincs_hmt"].layer["drainage_structures"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_drainage_structure", 0)
        update()
    app.model["sfincs_hmt"].drainage_structures_changed = False

def import_geojson(*args):

    map.reset_cursor()

    rsp = app.gui.window.dialog_open_file("Select file ...",
                                          filter="*.geojson",
                                          allow_directory_change=False)
    if rsp[0]:
        filename = rsp[0]
        gdf = gpd.read_file(filename)
        # Extract only LineStrings
        gdf = gdf[gdf.geometry.type == "LineString"].copy()
        # Check if there are any LineStrings
        if len(gdf) == 0:
            app.gui.window.dialog_warning("No LineString geometries found in the selected file.")
            return
        merge = False
        if app.model["sfincs_hmt"].domain.drainage_structures.nr_lines > 0:
            ok = app.gui.window.dialog_yes_no("Do you want to merge these with the existing drainage_structures?")
            if ok:
                merge = True
        app.model["sfincs_hmt"].domain.drainage_structures.set(gdf, merge=merge)
        app.map.layer["sfincs_hmt"].layer["drainage_structures"].set_data(gdf)
        app.gui.setvar("sfincs_hmt", "active_drainage_structure", 0)
        app.model["sfincs_hmt"].drainage_structures_changed = True
        update()

def save(*args):
    map.reset_cursor()
    filename = app.model["sfincs_hmt"].domain.config.get("thdfile")
    if not filename:
        filename = "sfincs.drn"
    rsp = app.gui.window.dialog_save_file("Select file ...",
                                          file_name=filename,
                                          filter="*.drn",
                                          allow_directory_change=False)
    if rsp[0]:
        app.model["sfincs_hmt"].domain.config.set("thdfile", rsp[2]) # file name without path
        app.model["sfincs_hmt"].domain.drainage_structures.write()
    app.model["sfincs_hmt"].drainage_structures_changed = False

def draw_drainage_structure(*args):
    # Need to ask what type of drainage structure to draw
    tp, ok = app.gui.window.dialog_popupmenu("Select drainage structure type", title="Drainage structure type", options=app.gui.getvar("sfincs_hmt", "drainage_structure_type_names"))
    if not ok:
        return
    # Find index of selected type in list of name
    index = app.gui.getvar("sfincs_hmt", "drainage_structure_type_names").index(tp)
    # Find corresponding type value
    type_to_add = app.gui.getvar("sfincs_hmt", "drainage_structure_types")[index]
    app.gui.setvar("sfincs_hmt", "drainage_structure_type_to_add", type_to_add)
    # And draw
    app.map.layer["sfincs_hmt"].layer["drainage_structures"].draw()

def delete_drainage_structure(*args):
    gdf = app.model["sfincs_hmt"].domain.drainage_structures.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar("sfincs_hmt", "drainage_structure_index")
    # Delete from map
    app.map.layer["sfincs_hmt"].layer["drainage_structures"].delete_feature(index)
    # Delete from app
    app.model["sfincs_hmt"].domain.drainage_structures.delete(index)
    app.model["sfincs_hmt"].drainage_structures_changed = True
    update()

def select_drainage_structure(*args):
    """Callback for selecting from list"""

    update()

def edit_drainage_structure_parameter(*args):
    """Callback for editing a parameter of the drainage structure"""

    index = app.gui.getvar("sfincs_hmt", "drainage_structure_index")
    tp = app.gui.getvar("sfincs_hmt", "drainage_structure_type")
    if tp == 1:
        # Pump
        par1 = app.gui.getvar("sfincs_hmt", "drainage_structure_discharge")
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 2:
        # Culvert
        par1 = app.gui.getvar("sfincs_hmt", "drainage_structure_alpha")
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 3:
        # Check valve
        par1 = app.gui.getvar("sfincs_hmt", "drainage_structure_alpha")
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 4:
        # Gate
        par1 = app.gui.getvar("sfincs_hmt", "drainage_structure_width")
        par2 = app.gui.getvar("sfincs_hmt", "drainage_structure_sill_elevation")
        par3 = app.gui.getvar("sfincs_hmt", "drainage_structure_manning_n")
        par4 = app.gui.getvar("sfincs_hmt", "drainage_structure_zmin")
        par5 = app.gui.getvar("sfincs_hmt", "drainage_structure_zmax")
        par6 = app.gui.getvar("sfincs_hmt", "drainage_structure_closing_time")
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par1"] = par1
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par2"] = par2
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par3"] = par3
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par4"] = par4
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par5"] = par5
        app.model["sfincs_hmt"].domain.drainage_structures.data.at[index, "par6"] = par6

    app.model["sfincs_hmt"].drainage_structures_changed = True

def drainage_structure_created(gdf, index, id):

    # Get new gdf with the new drainage structure, and update the app
    gdf_new = gdf.iloc[[index]]
    # Drop everything except geometry, and reset index to avoid issues with merging
    gdf_new = gdf_new[["geometry"]].reset_index(drop=True)

    # Now get parameters for the new drainage structure from the GUI
    q = app.gui.getvar("sfincs_hmt", "drainage_structure_discharge")
    alpha = app.gui.getvar("sfincs_hmt", "drainage_structure_alpha")
    width = app.gui.getvar("sfincs_hmt", "drainage_structure_width")
    elev = app.gui.getvar("sfincs_hmt", "drainage_structure_sill_elevation")
    manning_n = app.gui.getvar("sfincs_hmt", "drainage_structure_manning_n")
    zmin = app.gui.getvar("sfincs_hmt", "drainage_structure_zmin")
    zmax = app.gui.getvar("sfincs_hmt", "drainage_structure_zmax")
    closing_time = app.gui.getvar("sfincs_hmt", "drainage_structure_closing_time")

    tp = app.gui.getvar("sfincs_hmt", "drainage_structure_type_to_add")

    if tp == 1:
        # Pump
        app.model["sfincs_hmt"].domain.drainage_structures.create(gdf_new,
                                                                  stype="pump",
                                                                  discharge=q,
                                                                  merge=True)
    elif tp == 2:
        # Culvert
        app.model["sfincs_hmt"].domain.drainage_structures.create(gdf_new,
                                                                  stype="culvert",
                                                                  alpha=alpha,
                                                                  merge=True)
    elif tp == 3:
        # Check valve
        app.model["sfincs_hmt"].domain.drainage_structures.create(gdf_new,
                                                                  stype="valve",
                                                                  alpha=alpha,
                                                                  merge=True)
    elif tp == 4:
        # Gate
        app.model["sfincs_hmt"].domain.drainage_structures.create(gdf_new,
                                                                  stype="gate",
                                                                  alpha=alpha,
                                                                  width=width,
                                                                  sill_elevation=elev,
                                                                  manning_n=manning_n,
                                                                  zmin=zmin,
                                                                  zmax=zmax,
                                                                  closing_time=closing_time,
                                                                  merge=True)

    nrt = app.model["sfincs_hmt"].domain.drainage_structures.nr_lines

    # Set active drainage structure to the new one    
    app.gui.setvar("sfincs_hmt", "drainage_structure_type", tp)
    app.gui.setvar("sfincs_hmt", "drainage_structure_index", nrt - 1)
    app.model["sfincs_hmt"].drainage_structures_changed = True

    # Line string have been cut back to the first and last point, so update the gdf with the new geometry
    gdf = app.model["sfincs_hmt"].domain.drainage_structures.gdf
    app.map.layer["sfincs_hmt"].layer["drainage_structures"].set_data(gdf)

    update()

def drainage_structure_modified(gdf, index, id):
    app.model["sfincs_hmt"].domain.drainage_structures.create(gdf, merge=False)
    app.model["sfincs_hmt"].drainage_structures_changed = True
    # # The gdf may have been modified in other ways than just the geometry, so update the gdf in the app
    # gdf = app.model["sfincs_hmt"].domain.drainage_structures.gdf
    # app.map.layer["sfincs_hmt"].layer["drainage_structures"].set_data(gdf)

def drainage_structure_selected(index):
    app.gui.setvar("sfincs_hmt", "drainage_structure_index", index)
    update()

def set_model_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()

def update():
    nrt = app.model["sfincs_hmt"].domain.drainage_structures.nr_lines
    app.gui.setvar("sfincs_hmt", "nr_drainage_structures", nrt)
    if app.gui.getvar("sfincs_hmt", "drainage_structure_index" ) > nrt - 1:
        app.gui.setvar("sfincs_hmt", "drainage_structure_index", max(nrt - 1, 0))
    app.gui.setvar("sfincs_hmt", "drainage_structure_names", app.model["sfincs_hmt"].domain.drainage_structures.list_names)
    index = app.gui.getvar("sfincs_hmt", "drainage_structure_index")
    if nrt == 0:
        app.gui.setvar("sfincs_hmt", "drainage_structure_type", 1)
    else:
        drainage_structure_type = app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].type
        app.gui.setvar("sfincs_hmt", "drainage_structure_type", drainage_structure_type)
        # And now set the parameters
        if drainage_structure_type == 1:
            # Pump
            app.gui.setvar("sfincs_hmt", "drainage_structure_discharge", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par1)
        elif drainage_structure_type == 2:
            # Culvert
            app.gui.setvar("sfincs_hmt", "drainage_structure_alpha", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par1)
        elif drainage_structure_type == 3:
            # Check valve
            app.gui.setvar("sfincs_hmt", "drainage_structure_alpha", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par1)
        elif drainage_structure_type == 4:
            # Gate
            app.gui.setvar("sfincs_hmt", "drainage_structure_width", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par1)
            app.gui.setvar("sfincs_hmt", "drainage_structure_sill_elevation", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par2)
            app.gui.setvar("sfincs_hmt", "drainage_structure_manning_n", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par3)
            app.gui.setvar("sfincs_hmt", "drainage_structure_zmin", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par4)
            app.gui.setvar("sfincs_hmt", "drainage_structure_zmax", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par5)
            app.gui.setvar("sfincs_hmt", "drainage_structure_closing_time", app.model["sfincs_hmt"].domain.drainage_structures.gdf.iloc[index].par6)

    app.gui.window.update()
