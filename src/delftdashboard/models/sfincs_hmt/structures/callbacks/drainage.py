from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    click_add_structure as click_add_general_structure,
)
from delftdashboard.models.sfincs_hmt.structures.callbacks.general_structures import (
    select as select_general,
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
from delftdashboard.app import app


def select(*args):
    select_general(*args)


class DrainageTypes:
    TYPES = {0: "Pump", 1: "Culvert"}

    @classmethod
    def get_type(cls, index):
        return cls.TYPES.get(index, "Unknown")

    @classmethod
    def get_type_lower(cls, index):
        return cls.get_type(index).lower()


def _set_gui_variables(include_selection_type=False):
    """Set the gui variables for the drainage structure type

    Parameters
    ----------
    include_selection_type : bool, optional
        Whether to include the selection type, by default False
    """

    app.gui.setvar("measures", "selected_structure_type", "drn")
    app.gui.setvar("measures", "selected_measure_category", "hydraulic")
    app.gui.setvar(
        "measures",
        "selected_measure_type",
        DrainageTypes.get_type_lower(app.gui.getvar("sfincs_hmt", "drainage_type")),
    )

    if include_selection_type:
        method = app.gui.getvar("sfincs_hmt", "structure_drainage_method_index")
        method_list = app.gui.getvar("sfincs_hmt", "structure_drainage_methods")
        if method_list[method] == "Draw LineString":
            app.gui.setvar("measures", "selected_measure_selection_type", "polyline")
        else:
            app.gui.setvar("measures", "selected_measure_selection_type", "import_area")


def click_add_structure(*args):
    """Callback for adding a drainage structure"""
    _set_gui_variables(include_selection_type=True)
    click_add_general_structure(*args)


def click_select_structure(*args):
    """Callback for selecting a drainage structure"""
    _set_gui_variables()
    click_select_general_structure(*args)


def click_delete_structure(*args):
    """Callback for deleting a drainage structure"""
    _set_gui_variables()
    click_delete_general_structure(*args)


def click_delete_all_structures(*args):
    """Callback for deleting all drainage structures"""
    _set_gui_variables()
    click_delete_general_all_structures(*args)
