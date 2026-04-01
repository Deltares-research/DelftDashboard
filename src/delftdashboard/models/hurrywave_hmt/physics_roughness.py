"""GUI callbacks for the HurryWave Physics > Roughness sub-tab."""

from typing import Any

from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the Roughness sub-tab."""
    map.update()
