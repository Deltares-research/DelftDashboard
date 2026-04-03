"""Generic toolbox base class and toolbox selection logic.

Provides ``GenericToolbox``, the base class for all DelftDashboard toolboxes,
and the ``select_toolbox`` helper used by the menu system.
"""

from typing import Optional

from delftdashboard.app import app


class GenericToolbox:
    """Base class for all DelftDashboard toolboxes.

    Subclasses override ``add_layers`` and ``set_crs`` to provide
    model-specific map layers and coordinate-system handling.
    """

    def __init__(self) -> None:
        self.callback_module_name: Optional[str] = None

    def select(self) -> None:
        """Activate this toolbox in the GUI and make its layers visible.

        Update the tab panel to show this toolbox's elements and ensure the
        correct callback module is wired up.
        """
        app.active_toolbox = self
        app.gui.setvar("menu", "active_toolbox_name", app.active_toolbox.name)

        # Get index of active model
        index = list(app.model).index(app.active_model.name)

        # Toolbox tab
        tab = app.gui.window.elements[index].tabs[0]

        # Set callback module
        tab.module = app.active_toolbox.callback_module
        tab.widget.parent().parent().setTabText(0, app.active_toolbox.long_name)

        # First remove old toolbox elements from first tab
        app.gui.window.elements[index].clear_tab(0)

        # Now add toolbox elements to first tab
        app.gui.window.add_elements_to_tree(self.element, tab, app.gui.window)
        app.gui.window.add_elements(tab.elements)

        # And select this tab
        app.gui.window.elements[index].widget.select_tab(0)

        # Make toolbox layer visible
        if self.name in app.map.layer:
            app.map.layer[self.name].show()

        app.gui.window.update()

    def add_layers(self) -> None:
        """Register map layers for this toolbox.

        Override in subclasses to add toolbox-specific layers.
        """

    def delete_layers(self) -> None:
        """Delete map layers for this toolbox.

        .. deprecated::
            Use ``clear_layers`` instead.
        """
        if self.name in app.map.layer:
            app.map.layer[self.name].delete()

    def clear_layers(self) -> None:
        """Clear data from map layers without deleting the layer objects."""
        if self.name in app.map.layer:
            app.map.layer[self.name].clear()

    def set_crs(self) -> None:
        """Update the coordinate reference system for this toolbox.

        Override in subclasses to handle CRS changes.
        """


def select_toolbox(toolbox_name: str) -> None:
    """Activate the named toolbox.

    Parameters
    ----------
    toolbox_name : str
        Key into ``app.toolbox`` identifying the toolbox to select.
    """
    app.active_toolbox = app.toolbox[toolbox_name]
    app.active_toolbox.select()
    app.info.update(toolbox_name)
