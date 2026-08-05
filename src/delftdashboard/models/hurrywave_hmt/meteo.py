"""GUI callbacks for the HurryWave Meteo tab.

The wind source selector (none / uniform / gridded / netcdf / spiderweb) is
derived from which ``*file`` entries are present in the config, and
switching the source clears the file entries of the other sources.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "hurrywave_hmt"
_GROUP = "hurrywave_hmt"

# Config keys per wind source. The spiderweb file is kept separate: it can
# be combined with a gridded background wind (spwmergefrac), so selecting
# another source does not clear it.
_WIND_KEYS = {
    "uniform": ["wndfile"],
    "gridded": ["amufile", "amvfile"],
    "netcdf": ["netamuamvfile"],
}


def select(*args: Any) -> None:
    """Activate the Meteo tab."""
    map.update()
    update_sources()
    app.gui.window.update()


def set_model_variables(*args: Any) -> None:
    """Copy current GUI variables back to the model config."""
    app.model[_MODEL].set_model_variables()


def update_sources() -> None:
    """Derive the wind source popup from the config file entries."""
    config = app.model[_MODEL].domain.config

    spiderweb = bool(config.get("spwfile"))
    if config.get("netamuamvfile"):
        wind = "netcdf"
    elif config.get("amufile") or config.get("amvfile"):
        wind = "gridded"
    elif config.get("wndfile"):
        wind = "uniform"
    elif spiderweb:
        wind = "spiderweb"
    else:
        wind = "none"
    app.gui.setvar(_GROUP, "wind_source", wind)


def select_wind_source(*args: Any) -> None:
    """Handle a change of the wind source popup."""
    selected = app.gui.getvar(_GROUP, "wind_source")
    config = app.model[_MODEL].domain.config
    for source, keys in _WIND_KEYS.items():
        if source == selected:
            continue
        for key in keys:
            if config.get(key):
                config.set(key, None, skip_validation=True)
                app.gui.setvar(_GROUP, key, None)
    app.gui.window.update()
