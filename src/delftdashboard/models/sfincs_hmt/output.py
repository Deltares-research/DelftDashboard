from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    map.update()
    app.map.layer["sfincs_hmt"].layer["region"].show()
    app.map.layer["sfincs_hmt"].layer["region"].deactivate()
    app.map.layer["sfincs_hmt"].layer["boundary_points"].activate()
    app.map.layer["sfincs_hmt"].layer["discharge_points"].activate()
    app.map.layer["sfincs_hmt"].layer["observation_points"].activate()    
    app.map.layer["sfincs_hmt"].layer["measures"].activate()    


def set_variables(*args):
    # All variables will be set
    app.model["sfincs_hmt"].set_model_variables()
