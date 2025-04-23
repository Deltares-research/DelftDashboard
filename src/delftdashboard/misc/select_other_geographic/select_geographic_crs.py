import os
import pyproj

# Should this be part of Guitares instead?

def select_geographic_crs(app):

    # Get a list of all CRS
    crs_info_list = pyproj.database.query_crs_info(auth_name=None, pj_types=None)

    crs_names = []
    for crs_info in crs_info_list:
        # Check if the CRS is a geographic CRS
        if crs_info.type.name.lower() == "geographic_2d_crs":
            crs_names.append(crs_info.name)

    # Set WGS 84 as the first item in the list
    if "WGS 84" in crs_names:
        wgs_84_index = crs_names.index("WGS 84")
        crs_names[0], crs_names[wgs_84_index] = crs_names[wgs_84_index], crs_names[0]        

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
    
    return pyproj.CRS(selected_name)
