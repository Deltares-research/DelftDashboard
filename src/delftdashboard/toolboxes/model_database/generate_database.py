"""GUI callbacks for the model database generate/view tab.

Handle collection selection, domain visualization, map updates,
and model activation from the database.
"""

import os
from typing import Any, Dict

import geopandas as gpd
import pandas as pd

from delftdashboard.app import app
from delftdashboard.operations import map

# from delftdashboard.operations.model import select_model


def select(*args: Any) -> None:
    """Activate the generate tab and show model boundaries on the map."""
    map.update()  # This hides all toolbox and model layers
    app.map.layer["model_database"].show()
    if app.gui.getvar("model_database", "show_sfincs"):
        app.map.layer["model_database"].layer["boundaries_sfincs"].show()
    else:
        app.map.layer["model_database"].layer["boundaries_sfincs"].hide()
    if app.gui.getvar("model_database", "show_hurrywave"):
        app.map.layer["model_database"].layer["boundaries_hurrywave"].show()
    else:
        app.map.layer["model_database"].layer["boundaries_hurrywave"].hide()


def select_collection(*args: Any) -> None:
    """Handle collection selection events (placeholder)."""


def use_collection(*args: Any) -> None:
    """Add the selected collection to the active list and update the map."""
    group = "model_database"

    # Collection to be added
    collection_name = app.gui.getvar(group, "active_available_collection_name")
    selected_collections = app.gui.getvar(group, "selected_collection_names")

    if collection_name in selected_collections:
        # If the collection is already selected, do nothing
        return

    selected_collections.append(collection_name)
    app.gui.setvar(group, "active_selected_collection_name", collection_name)
    app.gui.setvar(group, "selected_collection_names", selected_collections)

    update_domains()


def remove_collection(*args: Any) -> None:
    """Remove the selected collection from the active list."""
    group = "model_database"

    # Names of selected collections
    names = app.gui.getvar(group, "selected_collection_names")
    if not names:
        return
    # Name of the collection to be removed
    name = app.gui.getvar(group, "active_selected_collection_name")

    # Remove name from names list
    names.remove(name)

    # Set new active selected collection name
    if not names:
        app.gui.setvar(group, "active_selected_collection_name", "")
    else:
        # Use first of list
        app.gui.setvar(group, "active_selected_collection_name", names[0])

    app.gui.setvar(group, "selected_collection_names", names)

    update_domains()


def select_selected_collections(*args: Any) -> None:
    """Handle selected-collections list click events (placeholder)."""


def update_domains(*args: Any) -> None:
    """Update the domain list from all selected collections."""
    group = "model_database"
    domain_names_all = []
    # Loop through all selected collections and make list of all domain names to be shown
    for collection_name in app.gui.getvar(group, "selected_collection_names"):
        domain_names_in_collection, _, _ = app.model_database.model_names(
            collection=collection_name
        )
        for domain_name_i in domain_names_in_collection:
            domain_names_all.append(domain_name_i)
    # Set the list of all domain names for the listbox
    app.gui.setvar(group, "domain_names", domain_names_all)
    # Set first domain name as selected
    active_domain_name = domain_names_all[0] if domain_names_all else ""
    app.gui.setvar(group, "active_domain_name", active_domain_name)

    # Update the map
    update_map()


def toggle_sfincs(*args: Any) -> None:
    """Toggle visibility of SFINCS model boundaries on the map."""
    viz = app.gui.getvar("model_database", "show_sfincs")
    if viz:
        app.map.layer["model_database"].layer["boundaries_sfincs"].show()
    else:
        app.map.layer["model_database"].layer["boundaries_sfincs"].hide()


def toggle_hurrywave(*args: Any) -> None:
    """Toggle visibility of HurryWave model boundaries on the map."""
    viz = app.gui.getvar("model_database", "show_hurrywave")
    if viz:
        app.map.layer["model_database"].layer["boundaries_hurrywave"].show()
    else:
        app.map.layer["model_database"].layer["boundaries_hurrywave"].hide()


def select_domain_from_list(*args: Any) -> None:
    """Highlight the map polygon corresponding to the selected domain in the list."""
    # Activate the polygon on the map
    group = "model_database"
    name = app.gui.getvar(group, "active_domain_name")
    model = app.model_database.get_model(name=name)

    if model.type == "sfincs":
        app.map.layer["model_database"].layer["boundaries_sfincs"].select_by_property(
            "name", name
        )
    elif model.type == "hurrywave":
        app.map.layer["model_database"].layer[
            "boundaries_hurrywave"
        ].select_by_property("name", name)

    return


def activate_domain(self) -> None:
    """Copy the selected domain input files and activate the model."""
    group = "model_database"

    # Check if the current working directory is an empty folder
    if os.listdir(os.getcwd()):
        ok = app.gui.window.dialog_yes_no(
            "The current working directory is not empty. This may overwrite existing files! It is strongly recommended to select an empty working directory. Do you want to continue?"
        )
        if not ok:
            return

    # Copy input files from the selected domain to the current working directory
    domain_name = app.gui.getvar(group, "active_domain_name")
    domain = app.model_database.get_model(name=domain_name)
    app.model_database.copy_model_input_files(domain_name, os.getcwd())

    # Now check what sort of model we are dealing with
    if domain.type == "sfincs":
        app.active_model = app.model["sfincs_cht"]
        app.active_model.select()
        app.active_model.open(filename="sfincs.inp")
    elif domain.type == "hurrywave":
        app.active_model = app.model["hurrywave"]
        app.active_model.select()
        app.active_model.open(filename="hurrywave.inp")


def update_map(*args) -> None:
    update_boundaries_on_map()


def update_boundaries_on_map(*args: Any) -> None:
    """Load and display model domain boundaries for all selected collections."""
    # Make list of all the domains
    all_model_names = app.gui.getvar("model_database", "domain_names")

    if not all_model_names:
        # If no models are selected, clear the map layers
        app.map.layer["model_database"].layer["boundaries_sfincs"].clear()
        app.map.layer["model_database"].layer["boundaries_hurrywave"].clear()
        return

    sfincs_models = []
    hurrywave_models = []

    for model_name in all_model_names:
        model = app.model_database.get_model(name=model_name)

        if model.type == "sfincs":
            sfincs_models.append(model)
        elif model.type == "hurrywave":
            hurrywave_models.append(model)

    # Waitbox

    wb = app.gui.window.dialog_wait("Loading domains...")

    # SFINCS models
    gdf_sfincs = gpd.GeoDataFrame()
    for m in sfincs_models:
        gdf = m.get_model_gdf()
        gdf["type"] = m.type  # Tag with model type
        gdf_sfincs = pd.concat([gdf_sfincs, gdf])

    if gdf_sfincs.empty:
        app.map.layer["model_database"].layer["boundaries_sfincs"].clear()
    else:
        gdf_sfincs.reset_index(drop=True, inplace=True)
        app.map.layer["model_database"].layer["boundaries_sfincs"].set_data(gdf_sfincs)
        if app.gui.getvar("model_database", "show_sfincs"):
            app.map.layer["model_database"].layer["boundaries_sfincs"].show()
        else:
            app.map.layer["model_database"].layer["boundaries_sfincs"].hide()

    # HurryWave models
    gdf_hurrywave = gpd.GeoDataFrame()
    for m in hurrywave_models:
        gdf = m.get_model_gdf()
        gdf["type"] = m.type  # Tag with model type
        gdf_hurrywave = pd.concat([gdf_hurrywave, gdf])

    if gdf_hurrywave.empty:
        app.map.layer["model_database"].layer["boundaries_hurrywave"].clear()
    else:
        gdf_hurrywave.reset_index(drop=True, inplace=True)
        app.map.layer["model_database"].layer["boundaries_hurrywave"].set_data(
            gdf_hurrywave
        )
        if app.gui.getvar("model_database", "show_hurrywave"):
            app.map.layer["model_database"].layer["boundaries_hurrywave"].show()
        else:
            app.map.layer["model_database"].layer["boundaries_hurrywave"].hide()

    wb.close()


def select_model_from_map(feature: Dict[str, Any], layer: Any) -> None:
    """Set the active domain name from a map click.

    Parameters
    ----------
    feature : Dict[str, Any]
        The clicked feature with properties.
    layer : Any
        Map layer that triggered the selection.
    """
    app.gui.setvar(
        "model_database", "active_domain_name", feature["properties"]["name"]
    )

    app.gui.window.update()
