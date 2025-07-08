
from delftdashboard.app import app
from delftdashboard.operations import map

def select_tab(self) -> None:
    """
    Select the model_database tab and update the map.
    """
    map.update()
    app.map.layer["model_database"].show()
    app.map.layer["model_database"].layer["boundaries"].activate()
    

def select_collection(*args):
    collection = args[0]
    model_names, _, _ = app.model_database.model_names(collection=collection)
    group = "model_database"
    app.gui.setvar(group, "model_names", model_names)
    app.gui.setvar(group, "model_index", 0)

def select_model(*args):
    pass


def select_selected_models(*args):
    update()

def update():
    group = "model_database"
    # Get the selected model names from the GUI
    selected_names = []
    nrd = len(app.selected_models)
    if nrd>0:
        for model in app.selected_models:
            # selected_names.append(dataset["dataset"].name)
            selected_names.append(model["name"])
        app.gui.setvar(group, "selected_model_names", selected_names)
        index = app.gui.getvar(group, "selected_model_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.selected_models[index]
        app.gui.setvar(group, "model_index", index)
    else:
        app.gui.setvar(group, "selected_model_names", [])
        app.gui.setvar(group, "model_index", 0)
    app.gui.setvar(group, "nr_selected_models", nrd)

    # Get selected collection
    #app.gui.setvar(group, "active_collection", selected_names)

def update_map(*args) -> None:
    app.toolbox["model_database"].update_boundaries_on_map()
