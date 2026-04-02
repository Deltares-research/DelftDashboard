"""Generic model base class and model selection logic.

Provides ``GenericModel``, the base class for all DelftDashboard models,
and the ``select_model`` helper used by the menu system.
"""

from typing import Any, Dict, Optional

from delftdashboard.app import app
from delftdashboard.operations.toolbox import select_toolbox


class GenericModel:
    """Base class for all DelftDashboard models.

    Subclasses override ``open``, ``add_layers``, ``get_view_menu``,
    ``set_view_menu``, and ``set_crs`` for model-specific behaviour.
    """

    def __init__(self) -> None:
        self.name: str = "model"
        self.long_name: str = "Model"
        self.exe_path: Optional[str] = None

    def open(self) -> None:
        """Open an existing model from disk.

        Override in subclasses to implement model-specific file loading.
        """

    def add_layers(self) -> None:
        """Register map layers for this model.

        Override in subclasses to add model-specific layers.
        """

    def clear_layers(self) -> None:
        """Clear model layers on the map, keeping the layer objects for reuse."""
        # Check if app actually has a map and layer, because this method is
        # also called during initialization before the map and layers are created.
        if hasattr(app, "map") and hasattr(app.map, "layer"):
            if self.name in app.map.layer:
                app.map.layer[self.name].clear()

    def select(self) -> None:
        """Activate this model in the GUI and update menus and layers.

        Set the correct tab panel visible, rebuild the toolbox menu for
        toolboxes compatible with this model, and show the model's map layers.
        """
        elements = app.gui.window.elements

        # Set tab panel for current model to visible
        for element in elements:
            if element.style == "tabpanel":
                if element.id == self.name:
                    element.widget.setVisible(True)
                    element.visible = True
        # And the others to invisible
        for element in elements:
            if element.style == "tabpanel":
                if element.id != self.name:
                    element.widget.setVisible(False)
                    element.visible = False

        app.active_model = self
        app.gui.setvar("menu", "active_model_name", app.active_model.name)

        # Check which toolboxes we can add and update the menu
        toolboxes_to_add = []
        for toolbox_name in app.toolbox:
            if toolbox_name in self.toolbox:
                toolboxes_to_add.append(toolbox_name)

        # Clear toolbox menu
        toolbox_menu = app.gui.window.menus[2]
        toolbox_menu.widget.clear()

        # Add toolboxes_to_add
        menu_to_add = []
        for toolbox_name in toolboxes_to_add:
            dependency = [
                {
                    "action": "check",
                    "checkfor": "all",
                    "check": [
                        {
                            "variable": "active_toolbox_name",
                            "operator": "eq",
                            "value": toolbox_name,
                        }
                    ],
                }
            ]
            menu_to_add.append(
                {
                    "text": app.toolbox[toolbox_name].long_name,
                    "variable_group": "menu",
                    "module": "delftdashboard.menu.toolbox",
                    "method": "select",
                    "id": toolbox_name,
                    "option": toolbox_name,
                    "checkable": True,
                    "dependency": dependency,
                }
            )
        toolbox_menu.menus = []
        app.gui.window.add_menu_to_tree(toolbox_menu.menus, menu_to_add, toolbox_menu)
        app.gui.window.add_menus(toolbox_menu.menus, toolbox_menu, app.gui)

        # Check if the current toolbox is available. If not, select a new toolbox.
        if app.active_toolbox.name in toolboxes_to_add:
            # Select active toolbox
            select_toolbox(app.active_toolbox.name)
        else:
            # Select first toolbox from the list
            select_toolbox(toolboxes_to_add[0])

        # Make model layer visible
        app.map.layer[self.name].show()

        # Set working directory to model path
        # sfincs_cht and hurrywave domains have a path, but sfincs_hmt does not.
        # Maybe the generic model object should have a path?
        # First just check if the model has a path, and if so, change to it.
        # TODO: maybe add a path attribute to the generic model object, and set
        # it to None if there is no path. Then we can just check if the path is
        # not None.
        # Following lines give error with HydroMT-SFINCS
        # if hasattr(app.active_model.domain, "path"):
        #     os.chdir(app.active_model.domain.path)

        app.gui.window.update()

    def get_view_menu(self) -> Dict[str, Any]:
        """Return the View menu configuration for this model.

        Override in subclasses to add model-specific view menu entries.

        Returns
        -------
        dict
            Menu configuration dictionary, or empty dict if none.
        """
        return {}

    def set_view_menu(self) -> None:
        """Apply View menu state for this model.

        Override in subclasses to handle view menu changes.
        """

    def set_crs(self) -> None:
        """Update the coordinate reference system for this model.

        Override in subclasses to handle CRS changes.
        """


def select_model(model_name: str) -> None:
    """Activate the named model.

    Parameters
    ----------
    model_name : str
        Key into ``app.model`` identifying the model to select.
    """
    app.active_model = app.model[model_name]
    app.model[model_name].select()
