"""GUI callbacks for the model database view tab.

Handle collection and model selection for viewing database entries.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map


def select_tab(self) -> None:
    """Activate the view tab and show model boundaries."""
    map.update()
    app.map.layer["model_database"].show()
    app.map.layer["model_database"].layer["boundaries"].activate()


def select_collection(*args: Any) -> None:
    """Update the model list when a collection is selected."""
    collection = args[0]
    model_names, _, _ = app.model_database.model_names(collection=collection)
    group = "model_database"
    app.gui.setvar(group, "model_names", model_names)
    app.gui.setvar(group, "model_index", 0)


def select_model(*args: Any) -> None:
    """Handle model selection events (placeholder)."""


def select_selected_models(*args: Any) -> None:
    """Refresh the view when selected models change."""
    update()


def update() -> None:
    """Synchronize the GUI state with the current model selection."""
    group = "model_database"
    # Get the selected model names from the GUI
    selected_names = []
    nrd = len(app.selected_models)
    if nrd > 0:
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
    # app.gui.setvar(group, "active_collection", selected_names)


def update_map(*args: Any) -> None:
    """Refresh model boundaries on the map."""
    app.toolbox["model_database"].update_boundaries_on_map()
