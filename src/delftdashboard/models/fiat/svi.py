from delftdashboard.app import app
from delftdashboard.operations import map

from pathlib import Path


def select(*args):
    # De-activate existing layers
    map.update()
    if  all(values.data is None for key, values in app.map.layer["buildings"].layer.items()):
        app.map.layer["modelmaker_fiat"].layer[app.gui.getvar("modelmaker_fiat", "active_area_of_interest")].show()

    app.gui.setvar("_main", "show_fiat_checkbox", True)


def edit(*args):
    app.active_model.set_model_variables()


def add_svi(*args):
    group = "fiat"

    # Get the variables
    census_key_path = Path(app.config_path) / "census_key.txt"
    if census_key_path.exists():
        fid = open(census_key_path, "r")
        census_key = fid.readlines()
        fid.close()

    census_key = census_key[0]
    year_data = app.gui.getvar(group, "selected_year")

    if app.gui.getvar(group, "use_svi"):
        app.active_model.domain.svi_vm.set_svi_settings(census_key, year_data)

    if app.gui.getvar(group, "use_equity"):
        app.active_model.domain.svi_vm.set_equity_settings(census_key, year_data)

    if app.gui.getvar(group, "use_svi") or app.gui.getvar(group, "use_equity"):
        app.gui.setvar("_main", "checkbox_svi_(optional)", True)

    app.gui.window.dialog_info(
        text="\nSVI and/or equity information were added to the model",
        title="Added SVI and/or equity",
    )
