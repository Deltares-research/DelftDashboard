from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def edit(*args):
    app.model["fiat"].set_model_variables()


def add_svi(*args):
    group = "fiat"

    # Get the variables
    census_key = ""
    state_abbreviation = app.gui.getvar(
        group, "selected_state"
    )  # Change to state identifier instead of name
    year_data = int(app.gui.getvar(group, "selected_year"))
    county = app.gui.getvar(group, "selected_county")

    if app.gui.getvar(group, "use_svi"):
        app.model["fiat"].domain.svi_vm.set_svi_settings(
            census_key, state_abbreviation, year_data, county
        )
    
    if app.gui.getvar(group, "use_equity"):
        app.model["fiat"].domain.svi_vm.set_equity_settings(
            census_key, state_abbreviation, year_data, county
        )
    
    if app.gui.getvar(group, "use_svi") or app.gui.getvar(group, "use_equity"):
        app.gui.setvar("group", "checkbox_svi_(optional)", True)

