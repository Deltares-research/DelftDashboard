"""GUI callbacks for the SFINCS HydroMT Meteo tab.

Wind, atmospheric pressure and rain each have their own source selector
(none / uniform / gridded / netcdf / spiderweb); the spiderweb file and its
parameters are shared between the three quantities. The source popups are
derived from which ``*file`` entries are present in the config, and
switching a source clears the file entries of the other sources for that
quantity.
"""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_MODEL = "sfincs_hmt"
_GROUP = "sfincs_hmt"

# Config keys per quantity and per source. Used both to derive the source
# popups from the config and to clear stale entries when the user switches
# a quantity to a different source. The spiderweb file itself is shared
# between quantities and therefore never cleared here.
_WIND_KEYS = {
    "uniform": ["wndfile"],
    "gridded": ["amufile", "amvfile"],
    "netcdf": ["netamuamvfile"],
}
_PRESSURE_KEYS = {
    "gridded": ["ampfile"],
    "netcdf": ["netampfile"],
}
_RAIN_KEYS = {
    "uniform": ["prcfile", "precipfile"],
    "gridded": ["amprfile"],
    "netcdf": ["netamprfile"],
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
    """Derive the three source popups from the config file entries."""
    config = app.model[_MODEL].domain.config

    # Migrate the legacy precipfile key to prcfile so the GUI (and the
    # written sfincs.inp) use the modern keyword.
    if config.get("precipfile") and not config.get("prcfile"):
        config.set("prcfile", config.get("precipfile"))
        config.set("precipfile", None)
        app.gui.setvar(_GROUP, "prcfile", config.get("prcfile"))
        app.gui.setvar(_GROUP, "precipfile", None)

    spiderweb = bool(config.get("spwfile") or config.get("netspwfile"))

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

    if config.get("netampfile"):
        pressure = "netcdf"
    elif config.get("ampfile"):
        pressure = "gridded"
    elif spiderweb:
        pressure = "spiderweb"
    else:
        pressure = "none"

    if config.get("netamprfile"):
        rain = "netcdf"
    elif config.get("amprfile"):
        rain = "gridded"
    elif config.get("prcfile"):
        rain = "uniform"
    elif spiderweb and config.get("usespwprecip"):
        rain = "spiderweb"
    else:
        rain = "none"

    app.gui.setvar(_GROUP, "wind_source", wind)
    app.gui.setvar(_GROUP, "pressure_source", pressure)
    app.gui.setvar(_GROUP, "rain_source", rain)


def _clear_other_sources(keys_by_source: dict, selected: str) -> None:
    """Clear the config file entries of the non-selected sources.

    The matching GUI variables are cleared as well so the next full
    GUI-to-config resync does not restore them.
    """
    config = app.model[_MODEL].domain.config
    for source, keys in keys_by_source.items():
        if source == selected:
            continue
        for key in keys:
            if config.get(key):
                config.set(key, None)
                app.gui.setvar(_GROUP, key, None)


def select_wind_source(*args: Any) -> None:
    """Handle a change of the wind source popup."""
    _clear_other_sources(_WIND_KEYS, app.gui.getvar(_GROUP, "wind_source"))
    app.gui.window.update()


def select_pressure_source(*args: Any) -> None:
    """Handle a change of the pressure source popup."""
    _clear_other_sources(_PRESSURE_KEYS, app.gui.getvar(_GROUP, "pressure_source"))
    app.gui.window.update()


def select_rain_source(*args: Any) -> None:
    """Handle a change of the rain source popup."""
    source = app.gui.getvar(_GROUP, "rain_source")
    _clear_other_sources(_RAIN_KEYS, source)
    # The spiderweb carries rain only when usespwprecip is on
    config = app.model[_MODEL].domain.config
    if source == "spiderweb":
        config.set("usespwprecip", 1, skip_validation=True)
        app.gui.setvar(_GROUP, "usespwprecip", 1)
    app.gui.window.update()
