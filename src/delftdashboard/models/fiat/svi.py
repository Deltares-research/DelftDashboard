from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def edit(*args):
    app.active_model.set_model_variables()


def add_svi(*args):
    group = "fiat"

    # Get the variables
    census_key = "495a349ce22bdb1294b378fb199e4f27e57471a9"  ## TODO: CHANGE TO INPUT
    state_abbreviation = "SC"  ## TODO: CHANGE TO INPUT
    year_data = 2021  ## TODO: CHANGE TO INPUT
    county = "019"  ## TODO: CHANGE TO INPUT

    if app.gui.getvar(group, "use_svi"):
        app.active_model.domain.svi_vm.set_svi_settings(
            census_key, state_abbreviation, year_data, county
        )
    
    if app.gui.getvar(group, "use_equity"):
        app.active_model.domain.svi_vm.set_equity_settings(
            census_key, state_abbreviation, year_data, county
        )
    
    if app.gui.getvar(group, "use_svi") or app.gui.getvar(group, "use_equity"):
        app.gui.setvar("group", "checkbox_svi_(optional)", True)

    app.gui.window.dialog_info(
        text="SVI and/or equity information were added to the model",
        title="Added SVI and/or equity",
    )
