import os
import pyproj

# Should this be part of Guitares instead?

def select_projected_crs(app):

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
    
    return pyproj.CRS(selected_name)
