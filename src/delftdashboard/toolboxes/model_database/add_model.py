import os
import shutil
from delftdashboard.app import app
from delftdashboard.operations import map
import toml

def select(*args):
    """
    Select the model_database tab and update the map.
    """
    app.map.layer["model_database"].show()
    app.map.layer["model_database"].layer["boundaries_sfincs"].hide()
    app.map.layer["model_database"].layer["boundaries_hurrywave"].hide()
    # Do we really want to immediately add active model? I think a push button is better. What if there is no active model?
    # select_model(*args)

    if app.active_model is not None:
        # Set multiple GUI variables efficiently using a dictionary
        model_type = "sfincs" if app.active_model.name in ("sfincs_cht", "sfincs_hmt") else app.active_model.name 
        gui_vars = {
            "active_model_name": app.gui.getvar("model_database", "active_domain_name"),
            "active_model_type": model_type,
            "active_model_crs": app.active_model.domain.crs.to_epsg(),
            "flow_nested": None,
            "flow_spinup_time": 24.0,
            "station": None,
            "make_flood_map": True,
            "make_water_level_map": True,
            "make_precipitation_map": True,
        }
        for key, value in gui_vars.items():
            app.gui.setvar("model_database", key, value)

def select_model(*args):
    """
    Select model to make model.toml.
    """
    group = "model_database"
    # Get the selected model names from the GUI
    if app.active_model.domain.grid.data is not None:
        # If a model is already active, prompt to select a new model
        wb = app.gui.window.dialog_wait("A model is already active")
        app.active_model.domain.mask.get_datashader_dataframe()
        app.active_model.plot()  
    else:
        wb = app.gui.window.dialog_wait("Choose domain to activate...")
        app.active_model.open()

    assert app.active_model.domain.grid.data is not None, "app.active_model.domain.grid.data is None"

    wb.close()
    wb = app.gui.window.dialog_wait("Loading metadata")

    # Get the model name from the GUI


    wb.close()

def set_collection_toml(*args):
 
    """ Set the collection toml file for the model.
    """
    pass

def set_nested(*args):

    """ Set the nested toml file for the model.
    """
    pass

    
def write_toml_file(self) -> None:
    """
    Make toml file for the model.
    """
    group = "model_database"
    # Get the model name from the GUI

    model_data = {
        "active_model_name": app.gui.getvar(group, "active_model_name"),
        "active_model_type": app.gui.getvar(group, "active_model_type"),
        "active_model_crs": app.gui.getvar(group, "active_model_crs"),
        "flow_nested": app.gui.getvar(group, "flow_nested"),
        "flow_spinup_time": app.gui.getvar(group, "flow_spinup_time"),
        "station": app.gui.getvar(group, "station"),
        "make_flood_map": app.gui.getvar(group, "make_flood_map"),
        "make_water_level_map": app.gui.getvar(group, "make_water_level_map"),
        "make_precipitation_map": app.gui.getvar(group, "make_precipitation_map"),
    }

    model_name = model_data["active_model_name"] or "model"

    # Construct model folder path
    collection_name = app.gui.getvar(group, "selected_collection_toml")
    model_type = app.gui.getvar(group, "active_model_type")
    model_folder_db = os.path.join(app.model_database.path, collection_name, model_type, model_name)
    os.makedirs(model_folder_db, exist_ok=True)

    toml_path = os.path.join(model_folder_db, "model.toml")
    with open(toml_path, "w") as toml_file:
        toml.dump(model_data, toml_file)

    print(f"Model data for {model_name} written to {toml_path}")

    # Ensure input and misc folders exist under model type
    for subfolder in ("input", "misc"):
        os.makedirs(os.path.join(model_folder_db, subfolder), exist_ok=True)

    # Store model in input folder
    # Temporary edit app.active_model.path to model_database path and edit back, can this be done more efficiently? I dont see an path variable in cht_sfincs
    original_path = app.active_model.domain.path
    dst_path =  os.path.join(model_folder_db, "input")
    
    # Write model
    app.active_model.domain.path = dst_path
    app.active_model.domain.write() 

    if app.active_model.domain.subgrid:
        app.active_model.domain.subgrid.write()

    print(f"Model files written to {dst_path}")

    # change back the path
    app.active_model.domain.path = original_path

    # Store model exterior in misc folder

    misc_folder = os.path.join(model_folder_db, "misc")
    exterior_path = os.path.join(misc_folder, "exterior.geojson")

    app.active_model.domain.grid.exterior.to_file(exterior_path, driver="GeoJSON")

    print(f"Model exterior written to {exterior_path}")
