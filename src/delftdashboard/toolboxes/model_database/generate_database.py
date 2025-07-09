
from delftdashboard.app import app
from delftdashboard.operations import map
import numpy as np
import os 

def select(*args):
    """
    Select the model_database tab and update the map.
    """
    app.map.layer["model_database"].layer["boundaries"].show()
    map.update()

def select_collection(*args):
    # collection = args[0]
    # model_names, _, _ = app.model_database.model_names(collection=collection)
    # group = "model_database"
    # app.gui.setvar(group, "model_names", model_names)
    # app.gui.setvar(group, "model_index", 0)
    pass

def select_domain(*args):
    # collection = args[0]
    # model_names, _, _ = app.model_database.model_names(collection=collection)
    # group = "model_database"
    # app.gui.setvar(group, "model_names", model_names)
    # app.gui.setvar(group, "model_index", 0)
    pass


def use_collection(*args):
    group = "model_database"
    names = app.gui.getvar(group, "collection_names")
    index = app.gui.getvar(group, "collection_index")
    name  = names[index]
    if name not in app.gui.getvar(group, "selected_collection_names"):
        # d = bathymetry_database.get_dataset(name)
        collection = {"name": name}
        app.selected_collections.append(name)
        app.gui.setvar(group, "selected_collection_names", app.selected_collections)
        app.gui.setvar(group, "selected_collection_index", len(app.selected_collections) - 1)
        app.gui.setvar(group, "selected_collection_toml", app.selected_collections[0])


    domain_names_all= [] 
    for collection_name in app.selected_collections:
        domain_names_in_collection, _, _ = app.model_database.model_names(collection=collection_name)
        for domain_name_i in domain_names_in_collection:
            domain_names_all.append(domain_name_i)

    for name in domain_names_all:
        if name not in app.gui.getvar(group, "domain_names"):
            # d = bathymetry_database.get_dataset(name)
            collection = {"name": name}
            app.domains.append(name)
            app.gui.setvar(group, "domain_names", app.domains)
            app.gui.setvar(group, "domain_index", len(app.domains) - 1)
            app.gui.setvar(group, "domain_names_all", app.domains)
            app.gui.setvar(group, "domain_index_all", len(app.domains) - 1)


    update()


def remove_collection(*args):
    group = "model_database"
    names = app.gui.getvar(group, "selected_collection_names")
    index = app.gui.getvar(group, "selected_collection_index")
    name  = names[index]
    if name in app.gui.getvar(group, "selected_collection_names"):
        # d = bathymetry_database.get_dataset(name)
        collection = {"name": name}
        domain_names_in_collection, _, _ = app.model_database.model_names(collection=name)
        app.selected_collections.remove(name)
        app.gui.setvar(group, "selected_collection_index", len(app.selected_collections) - 1)

    domain_names_all= [] 

    for domain_name_i in domain_names_in_collection:
        domain_names_all.append(domain_name_i)

    for name in domain_names_all:
        if name in app.gui.getvar(group, "domain_names"):
            # d = bathymetry_database.get_dataset(name)
            collection = {"name": name}
            app.domains.remove(name)
            app.gui.setvar(group, "domain_names", app.domains)
            app.gui.setvar(group, "domain_index", len(app.domains) - 1)
            app.gui.setvar(group, "domain_names_all", app.domains)
            app.gui.setvar(group, "domain_index_all", len(app.domains) - 1)


    
    update()

def select_sfincs(*args):
    tag = app.gui.getvar("model_database", "select_sfincs")
    domain_names = app.gui.getvar("model_database", "domain_names")
    domain_names_all = app.gui.getvar("model_database", "domain_names_all")

    group = "model_database"

    # Get all models in domain_names_all and collect their types
    model_types = []
    for name in domain_names_all:
        # Assuming app.model_database.get_model_type returns the type for a given domain/model name
        model = app.model_database.get_model(name)
        model_types.append(model.type)

    if tag:
        # If sfincs is selected, filter domain_names to include sfincs models and all other in domain_names 
        app.domains = [name for name, model_type in zip(domain_names_all, model_types) if model_type == "sfincs" or name in domain_names]
    else:
        # If sfincs is not selected, filter domain_names to exclude sfincs models
        app.domains = [name for name, model_type in zip(domain_names_all, model_types) if model_type != "sfincs"]

    app.gui.setvar(group, "domain_names", app.domains)
    app.gui.setvar(group, "domain_index", len(app.domains) - 1)

    update_map()

def select_hurrywave(*args):
    tag = app.gui.getvar("model_database", "select_hurrywave")
    domain_names = app.gui.getvar("model_database", "domain_names")
    domain_names_all = app.gui.getvar("model_database", "domain_names_all")

    group = "model_database"

    # Get all models in domain_names_all and collect their types
    model_types = []
    for name in domain_names_all:
        # Assuming app.model_database.get_model_type returns the type for a given domain/model name
        model = app.model_database.get_model(name)
        model_types.append(model.type)

    if tag:
        # If sfincs is selected, filter domain_names to include sfincs models and all other in domain_names 
        app.domains = [name for name, model_type in zip(domain_names_all, model_types) if model_type == "hurrywave" or name in domain_names]
    else:
        # If sfincs is not selected, filter domain_names to exclude hurrywave models
        app.domains = [name for name, model_type in zip(domain_names_all, model_types) if model_type != "hurrywave"]

    app.gui.setvar(group, "domain_names", app.domains)
    app.gui.setvar(group, "domain_index", len(app.domains) - 1)

    update_map()

def select_selected_collections(*args):
    update()

def select_selected_domains(*args):
    app.selected_domains = []

    group = "model_database"
    names = app.gui.getvar(group, "domain_names")
    index = app.gui.getvar(group, "domain_index")
    name  = names[index]

    app.selected_domains = name
    app.gui.setvar(group, "selected_domain_names", app.selected_domains)
    app.gui.setvar(group, "selected_domain_index", len(app.selected_domains) - 1)

    update()

    
def activate_domain(self) -> None:
    """
    Select model to make model.toml.
    """
    group = "model_database"

    domain_name = app.gui.getvar(group, "selected_domain_names")
    domain = app.model_database.get_model(name=domain_name)
    # Get domain path robustly
    domain_path = getattr(domain, 'path', None)
    if not domain_path or not isinstance(domain_path, str):
        print(f"Invalid or missing domain path for domain: {domain_name}")
        return

    domain_input_folder = os.path.join(domain_path, "input")

    # Check if the input folder exists, else use the original domain_path
    if os.path.isdir(domain_input_folder):
        domain_path = domain_input_folder

    if domain_path is None:
        print("Domain path is not set for domain: ", domain_name)
        return
    
    domain_type = domain.type

    # Find corresponding model in app.model
    for model in app.model:
        dlg = app.gui.window.dialog_wait("Activating domain ...")
        app.active_model = app.model[model]

        os.chdir(domain.path)
        app.active_model.initialize()
        app.active_model.domain.path = domain_path
        app.active_model.domain.read()
        app.active_model.set_gui_variables()
        # Also get mask datashader dataframe (should this not happen when grid is read?)
        app.active_model.domain.mask.get_datashader_dataframe()
        if app.model["sfincs_cht"].domain.input.variables.snapwave:
            # If snapwave is used, get the datashader dataframe for the snapwave mask
            app.active_model.domain.snapwave.mask.get_datashader_dataframe()	

        # Change CRS
        map.set_crs(app.active_model.domain.crs)
        app.active_model.plot()
        dlg.close()
        app.gui.window.update()
        # Zoom to model extent
        bounds = app.active_model.domain.grid.bounds(crs=4326, buffer=0.1)
        app.map.fit_bounds(bounds[0], bounds[1], bounds[2], bounds[3])

    update_map()
    print("Domain name: ", domain_name)
    

def update():
    group = "model_database"
    # Get the selected model names from the GUI
    selected_names = []
    nrd = len(app.selected_collections)
    if nrd>0:
        index = app.gui.getvar(group, "selected_collection_index")
        for collection in app.selected_collections:
            selected_names.append(collection)
                                  
        app.gui.setvar(group, "selected_collection_names", selected_names)
        app.gui.setvar(group, "selected_collection_index", index)
        
    else:
        app.gui.setvar(group, "selected_collection_names", [])
        app.gui.setvar(group, "selected_collection_index", 0)

    app.gui.setvar(group, "nr_selected_collections", nrd)
    update_map()

    # Get selected collection
    #app.gui.setvar(group, "active_collection", selected_names)

def update_map(*args) -> None:
    app.toolbox["model_database"].update_boundaries_on_map()
