import os
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

    app.gui.setvar(group, "active_model_name", app.gui.getvar("model_database", "selected_domain_names"))
    app.gui.setvar(group, "active_model_type", app.active_model.name)      
    app.gui.setvar(group, "active_model_crs", app.active_model.domain.crs.to_epsg())

    app.gui.setvar(group, "flow_nested", None)
    app.gui.setvar(group, "flow_spinup_time", 24.0)
    app.gui.setvar(group, "station", None)

    app.gui.setvar(group, "make_flood_map", True)
    app.gui.setvar(group, "make_water_level_map", True)
    app.gui.setvar(group, "make_precipitation_map", True)
    wb.close()

def set_collection_toml(*args):
 
    """ Set the collection toml file for the model.
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

    # Go one directory up from the model path
    toml_path = os.path.join(os.path.dirname(app.active_model.domain.path), f"model_new.toml") # Include the collection here if needed

    with open(toml_path, "w") as toml_file:
        toml.dump(model_data, toml_file)

    print(f"Model data written to {toml_path}")