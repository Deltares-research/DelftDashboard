"""GUI callbacks for the SFINCS HydroMT Observation Points parent tab.

Handles tab selection for the observation points panel which contains
sub-tabs for observation points and cross sections.
"""

from typing import Any

from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the Observation Points tab and update map layers."""
    map.update()
