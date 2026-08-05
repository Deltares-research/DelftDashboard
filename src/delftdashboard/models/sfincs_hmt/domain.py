"""GUI callbacks for the SFINCS HydroMT Domain tab.

The tab is read-only: the grid attributes and refinement-level cell counts
are gathered from the quadtree grid itself (sfincs.nc), never from the GUI.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"


def select(*args: Any) -> None:
    """Activate the Domain tab and update map layers."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_MODEL].layer["mask"].activate()
    # Refresh the (read-only) grid attributes and refinement-level counts
    # from the quadtree grid itself
    app.model[_MODEL].update_domain_info()
    app.gui.window.update()


def select_refinement_level(*args: Any) -> None:
    """Selection in the refinement-level list (display only)."""
    pass
