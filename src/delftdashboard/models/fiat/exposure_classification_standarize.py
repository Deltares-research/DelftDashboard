# -*- coding: utf-8 -*-
from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.active_model.set_input_variables()


def assign_occupancy_type(*args):
    model = "fiat"

    # Get the exposure category
    object_type = app.gui.getvar(model, "object_type")
    active_exposure_category_standardize = app.gui.getvar(
        model, "active_exposure_category_standardize"
    )
    exposure_categories_to_standardize = app.gui.getvar(
        model, "exposure_categories_to_standardize"
    )
    exposure_category = list(
        exposure_categories_to_standardize[object_type]
        .iloc[active_exposure_category_standardize]
        .values
    )
    app.gui.setvar(
        model, "new_occupancy_type", exposure_category
    )
    
    # Get the hazus/iwr occupancy class
    active_related_occupancy_type = app.gui.getvar(
        model, "active_related_occupancy_type"
    )
    hazus_iwr_occupancy_classes = app.gui.getvar(model, "hazus_iwr_occupancy_classes")
    hazus_iwr_occupancy_class = (
        hazus_iwr_occupancy_classes["Occupancy Class"]
        .iloc[active_related_occupancy_type]
        .values[0]
    )
    app.gui.setvar(
        model, "old_occupancy_type", hazus_iwr_occupancy_class
    )

    # Assign the selected hazus/iwr occupancy class to the selected exposure category table and dictionary
    exposure_categories_to_standardize.loc[
        exposure_categories_to_standardize[object_type].isin(exposure_category),
        "Assigned",
    ] = hazus_iwr_occupancy_class
    app.gui.setvar(
        model, "exposure_categories_to_standardize", exposure_categories_to_standardize
    )

    for ec in exposure_category:
        app.active_model.default_dict_categories[ec] = hazus_iwr_occupancy_class
