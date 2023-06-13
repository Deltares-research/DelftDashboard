from delftdashboard.app import app


def select(*args):
    app.update_map()
    app.map.layer["sfincs_hmt"].layer["observation_points"].set_mode("active")


def edit(*args):
    app.model["sfincs_hmt"].set_model_variables()
