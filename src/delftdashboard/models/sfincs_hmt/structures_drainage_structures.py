"""GUI callbacks for the SFINCS HydroMT Drainage Structures sub-tab.

Handles drawing, editing, deleting, loading, saving, and importing
drainage structure polylines (pumps, culverts, check valves, and gates).
"""

from typing import Any

import geopandas as gpd

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Drainage Structures sub-tab and show polylines on map."""
    map.update()
    # Activate draw layer
    app.map.layer[_MODEL].layer["drainage_structures"].activate()
    update()


def deselect(*args: Any) -> None:
    """Prompt to save unsaved drainage structure changes when leaving the tab."""
    if app.model[_MODEL].drainage_structures_changed:
        if app.model[_MODEL].domain.drainage_structures.nr_lines == 0:
            # No drainage_structures, so just reset the flag and return
            app.model[_MODEL].drainage_structures_changed = False
            return
        ok = app.gui.window.dialog_yes_no(
            "The drainage_structures have changed. Would you like to save the changes?"
        )
        if ok:
            save()


def load(*args: Any) -> None:
    """Load drainage structures from a .drn file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    rsp = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="sfincs.drn",
        filter="*.drn",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("drnfile", rsp[2])
        app.model[_MODEL].domain.drainage_structures.read()
        gdf = app.model[_MODEL].domain.drainage_structures.gdf
        app.map.layer[_MODEL].layer["drainage_structures"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_drainage_structure", 0)
        update()
    app.model[_MODEL].drainage_structures_changed = False


def import_geojson(*args: Any) -> None:
    """Import drainage structures from a GeoJSON file, optionally merging.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()

    rsp = app.gui.window.dialog_open_file(
        "Select file ...", filter="*.geojson", allow_directory_change=False
    )
    if rsp[0]:
        filename = rsp[0]
        gdf = gpd.read_file(filename)
        # Extract only LineStrings
        gdf = gdf[gdf.geometry.type == "LineString"].copy()
        # Check if there are any LineStrings
        if len(gdf) == 0:
            app.gui.window.dialog_warning(
                "No LineString geometries found in the selected file."
            )
            return
        merge = False
        if app.model[_MODEL].domain.drainage_structures.nr_lines > 0:
            ok = app.gui.window.dialog_yes_no(
                "Do you want to merge these with the existing drainage_structures?"
            )
            if ok:
                merge = True
        app.model[_MODEL].domain.drainage_structures.set(gdf, merge=merge)
        app.map.layer[_MODEL].layer["drainage_structures"].set_data(gdf)
        app.gui.setvar(_GROUP, "active_drainage_structure", 0)
        app.model[_MODEL].drainage_structures_changed = True
        update()


def save(*args: Any) -> None:
    """Save drainage structures to a .drn file selected by the user.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.reset_cursor()
    filename = app.model[_MODEL].domain.config.get("thdfile")
    if not filename:
        filename = "sfincs.drn"
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=filename,
        filter="*.drn",
        allow_directory_change=False,
    )
    if rsp[0]:
        app.model[_MODEL].domain.config.set("thdfile", rsp[2])
        app.model[_MODEL].domain.drainage_structures.write()
    app.model[_MODEL].drainage_structures_changed = False


def draw_drainage_structure(*args: Any) -> None:
    """Prompt for the drainage structure type and start the map draw interaction.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    # Need to ask what type of drainage structure to draw
    tp, ok = app.gui.window.dialog_popupmenu(
        "Select drainage structure type",
        title="Drainage structure type",
        options=app.gui.getvar(_GROUP, "drainage_structure_type_names"),
    )
    if not ok:
        return
    # Find index of selected type in list of name
    index = app.gui.getvar(_GROUP, "drainage_structure_type_names").index(tp)
    # Find corresponding type value
    type_to_add = app.gui.getvar(_GROUP, "drainage_structure_types")[index]
    app.gui.setvar(_GROUP, "drainage_structure_type_to_add", type_to_add)
    # And draw
    app.map.layer[_MODEL].layer["drainage_structures"].draw()


def delete_drainage_structure(*args: Any) -> None:
    """Delete the currently selected drainage structure.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    gdf = app.model[_MODEL].domain.drainage_structures.gdf
    if len(gdf) == 0:
        return
    index = app.gui.getvar(_GROUP, "drainage_structure_index")
    # Delete from map
    app.map.layer[_MODEL].layer["drainage_structures"].delete_feature(index)
    # Delete from app
    app.model[_MODEL].domain.drainage_structures.delete(index)
    app.model[_MODEL].drainage_structures_changed = True
    update()


def select_drainage_structure(*args: Any) -> None:
    """Handle selection of a drainage structure from the GUI list."""
    update()


def edit_drainage_structure_parameter(*args: Any) -> None:
    """Write edited drainage structure parameters back to the model data.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    index = app.gui.getvar(_GROUP, "drainage_structure_index")
    tp = app.gui.getvar(_GROUP, "drainage_structure_type")
    if tp == 1:
        # Pump
        par1 = app.gui.getvar(_GROUP, "drainage_structure_discharge")
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 2:
        # Culvert
        par1 = app.gui.getvar(_GROUP, "drainage_structure_alpha")
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 3:
        # Check valve
        par1 = app.gui.getvar(_GROUP, "drainage_structure_alpha")
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par1"] = par1
    elif tp == 4:
        # Gate
        par1 = app.gui.getvar(_GROUP, "drainage_structure_width")
        par2 = app.gui.getvar(_GROUP, "drainage_structure_sill_elevation")
        par3 = app.gui.getvar(_GROUP, "drainage_structure_manning_n")
        par4 = app.gui.getvar(_GROUP, "drainage_structure_zmin")
        par5 = app.gui.getvar(_GROUP, "drainage_structure_zmax")
        par6 = app.gui.getvar(_GROUP, "drainage_structure_closing_time")
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par1"] = par1
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par2"] = par2
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par3"] = par3
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par4"] = par4
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par5"] = par5
        app.model[_MODEL].domain.drainage_structures.data.at[index, "par6"] = par6

    app.model[_MODEL].drainage_structures_changed = True


def drainage_structure_created(gdf: Any, index: int, id: Any) -> None:
    """Handle creation of a new drainage structure polyline on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all drainage structure features.
    index : int
        Index of the newly created feature.
    id : Any
        Feature identifier.
    """
    # Get new gdf with the new drainage structure, and update the app
    gdf_new = gdf.iloc[[index]]
    # Drop everything except geometry, and reset index to avoid issues with merging
    gdf_new = gdf_new[["geometry"]].reset_index(drop=True)

    # Now get parameters for the new drainage structure from the GUI
    q = app.gui.getvar(_GROUP, "drainage_structure_discharge")
    alpha = app.gui.getvar(_GROUP, "drainage_structure_alpha")
    width = app.gui.getvar(_GROUP, "drainage_structure_width")
    elev = app.gui.getvar(_GROUP, "drainage_structure_sill_elevation")
    manning_n = app.gui.getvar(_GROUP, "drainage_structure_manning_n")
    zmin = app.gui.getvar(_GROUP, "drainage_structure_zmin")
    zmax = app.gui.getvar(_GROUP, "drainage_structure_zmax")
    closing_time = app.gui.getvar(_GROUP, "drainage_structure_closing_time")

    tp = app.gui.getvar(_GROUP, "drainage_structure_type_to_add")

    if tp == 1:
        # Pump
        app.model[_MODEL].domain.drainage_structures.create(
            gdf_new, stype="pump", discharge=q, merge=True
        )
    elif tp == 2:
        # Culvert
        app.model[_MODEL].domain.drainage_structures.create(
            gdf_new, stype="culvert", alpha=alpha, merge=True
        )
    elif tp == 3:
        # Check valve
        app.model[_MODEL].domain.drainage_structures.create(
            gdf_new, stype="valve", alpha=alpha, merge=True
        )
    elif tp == 4:
        # Gate
        app.model[_MODEL].domain.drainage_structures.create(
            gdf_new,
            stype="gate",
            alpha=alpha,
            width=width,
            sill_elevation=elev,
            manning_n=manning_n,
            zmin=zmin,
            zmax=zmax,
            closing_time=closing_time,
            merge=True,
        )

    nrt = app.model[_MODEL].domain.drainage_structures.nr_lines

    # Set active drainage structure to the new one
    app.gui.setvar(_GROUP, "drainage_structure_type", tp)
    app.gui.setvar(_GROUP, "drainage_structure_index", nrt - 1)
    app.model[_MODEL].drainage_structures_changed = True

    # Line string have been cut back to the first and last point, so update the gdf with the new geometry
    gdf = app.model[_MODEL].domain.drainage_structures.gdf
    app.map.layer[_MODEL].layer["drainage_structures"].set_data(gdf)

    update()


def drainage_structure_modified(gdf: Any, index: int, id: Any) -> None:
    """Handle modification of an existing drainage structure polyline.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing all drainage structure features.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.model[_MODEL].domain.drainage_structures.create(gdf, merge=False)
    app.model[_MODEL].drainage_structures_changed = True
    # # The gdf may have been modified in other ways than just the geometry, so update the gdf in the app
    # gdf = app.model[_MODEL].domain.drainage_structures.gdf
    # app.map.layer[_MODEL].layer["drainage_structures"].set_data(gdf)


def drainage_structure_selected(index: int) -> None:
    """Handle selection of a drainage structure on the map.

    Parameters
    ----------
    index : int
        Index of the selected drainage structure.
    """
    app.gui.setvar(_GROUP, "drainage_structure_index", index)
    update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def update() -> None:
    """Refresh the drainage structure list, type, and parameters in the GUI."""
    nrt = app.model[_MODEL].domain.drainage_structures.nr_lines
    app.gui.setvar(_GROUP, "nr_drainage_structures", nrt)
    if app.gui.getvar(_GROUP, "drainage_structure_index") > nrt - 1:
        app.gui.setvar(_GROUP, "drainage_structure_index", max(nrt - 1, 0))
    app.gui.setvar(
        _GROUP,
        "drainage_structure_names",
        app.model[_MODEL].domain.drainage_structures.list_names,
    )
    index = app.gui.getvar(_GROUP, "drainage_structure_index")
    if nrt == 0:
        app.gui.setvar(_GROUP, "drainage_structure_type", 1)
    else:
        drainage_structure_type = (
            app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].type
        )
        app.gui.setvar(_GROUP, "drainage_structure_type", drainage_structure_type)
        # And now set the parameters
        if drainage_structure_type == 1:
            # Pump
            app.gui.setvar(
                _GROUP,
                "drainage_structure_discharge",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par1,
            )
        elif drainage_structure_type == 2:
            # Culvert
            app.gui.setvar(
                _GROUP,
                "drainage_structure_alpha",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par1,
            )
        elif drainage_structure_type == 3:
            # Check valve
            app.gui.setvar(
                _GROUP,
                "drainage_structure_alpha",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par1,
            )
        elif drainage_structure_type == 4:
            # Gate
            app.gui.setvar(
                _GROUP,
                "drainage_structure_width",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par1,
            )
            app.gui.setvar(
                _GROUP,
                "drainage_structure_sill_elevation",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par2,
            )
            app.gui.setvar(
                _GROUP,
                "drainage_structure_manning_n",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par3,
            )
            app.gui.setvar(
                _GROUP,
                "drainage_structure_zmin",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par4,
            )
            app.gui.setvar(
                _GROUP,
                "drainage_structure_zmax",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par5,
            )
            app.gui.setvar(
                _GROUP,
                "drainage_structure_closing_time",
                app.model[_MODEL].domain.drainage_structures.gdf.iloc[index].par6,
            )

    app.gui.window.update()
