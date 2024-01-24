from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    click_add_structure as click_add_general_structure,
)
from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    click_select_structure as click_select_general_structure,
)
from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    click_delete_structure as click_delete_general_structure,
)
from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    click_delete_all_structures as click_delete_general_all_structures,
)
from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    select as select_general,
)
from delftdashboard.app import app


def select(*args):
    _set_gui_variables()
    select_general(*args)


def _set_gui_variables(include_selection_type=False):
    """Set the gui variables for the dam structure type

    Parameters
    ----------
    include_selection_type : bool, optional
        Whether to include the selection type, by default False
    """

    app.gui.setvar("measures", "selected_structure_type", "thd")
    app.gui.setvar("measures", "selected_measure_category", "hydraulic")
    app.gui.setvar("measures", "selected_measure_type", "thin_dam")

    if include_selection_type:
        method = app.gui.getvar("sfincs_hmt", "structure_thin_dam_method_index")
        method_list = app.gui.getvar("sfincs_hmt", "structure_thin_dam_methods")
        if method_list[method] == "Draw LineString":
            app.gui.setvar("measures", "selected_measure_selection_type", "polyline")
        else:
            app.gui.setvar("measures", "selected_measure_selection_type", "import_area")


def click_add_structure(*args):
    """Callback for adding a dam structure"""
    _set_gui_variables(include_selection_type=True)
    click_add_general_structure(*args)


def click_select_structure(*args):
    """Callback for selecting a dam structure"""
    _set_gui_variables()
    click_select_general_structure(*args)


def click_delete_structure(*args):
    """Callback for deleting a dam structure"""
    _set_gui_variables()
    click_delete_general_structure(*args)


def click_delete_all_structures(*args):
    """Callback for deleting all dam structures"""
    _set_gui_variables()
    click_delete_general_all_structures(*args)
