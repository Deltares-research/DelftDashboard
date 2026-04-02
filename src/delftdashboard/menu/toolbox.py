"""Menu callbacks for switching the active toolbox."""

from delftdashboard.operations.toolbox import select_toolbox


def select(toolbox_name: str) -> None:
    """Select and activate a toolbox by name.

    Parameters
    ----------
    toolbox_name : str
        Name of the toolbox to select.
    """
    select_toolbox(toolbox_name)
    # app.active_toolbox = app.toolbox[toolbox_name]
    # app.active_toolbox.select()
