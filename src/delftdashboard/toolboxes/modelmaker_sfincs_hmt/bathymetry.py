import os
import yaml

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()
    # app.map.layer["sfincs_hmt"].layer["grid"].show()
    # app.map.layer["sfincs_hmt"].layer["grid"].deactivate()
    app.map.layer["sfincs_hmt"].layer["bed_levels"].show()
    app.map.layer["sfincs_hmt"].layer["bed_levels"].activate()

def select_bathymetry_source(*args):
    source = args[0]
    
    dataset_names = []
    # Bathymetry
    if app.config["data_libs"] is not None:
        for key in app.data_catalog.keys:
            # only keep raster datasets
            if app.data_catalog[key].driver == "raster":
                # only keep topography datasets
                if app.data_catalog[key].meta["category"] == "topography":
                    # retrieve source name
                    if app.data_catalog[key].meta["source"] == source:
                        dataset_names.append(key)

    app.gui.setvar("modelmaker_sfincs_hmt", "bathymetry_dataset_names", dataset_names)
    app.gui.setvar("modelmaker_sfincs_hmt", "bathymetry_dataset_index", 0)
    
    name = dataset_names[0]
    meta = app.data_catalog[name].meta
    meta_str = yaml.dump(meta, default_flow_style=False)
    app.gui.setvar("modelmaker_sfincs_hmt", "selected_bathymetry_dataset_meta", meta_str)

def select_bathymetry_dataset(*args):
    pass

def info_selected_dataset(*args):
    toolbox_name = "modelmaker_sfincs_hmt"

    # show pop-up with some metadata of the selected dataset
    index = app.gui.getvar(toolbox_name, "bathymetry_dataset_index")
    name = app.gui.getvar(toolbox_name, "bathymetry_dataset_names")[index]

    meta = app.data_catalog[name].meta
    meta_str = yaml.dump(meta, default_flow_style=False)
    app.gui.setvar(toolbox_name, "selected_bathymetry_dataset_meta", meta_str)    

    path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
    pop_win_config_path  = os.path.join(path, "bathymetry_info.yml")
    okay, data = app.gui.popup(pop_win_config_path , None)
    if not okay:
        return
    
def use_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    name = names[index]
    if name not in app.gui.getvar(group, "selected_bathymetry_dataset_names"):
        dataset = {"elevtn": name, "zmin": -99999.0, "zmax": 99999.0, "offset": 0}
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets.append(
            dataset
        )
        app.gui.setvar(
            group,
            "selected_bathymetry_dataset_index",
            len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) - 1,
        )
        update()


def select_selected_bathymetry_dataset(*args):
    update()


def remove_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) == 0:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets.pop(index)
    update()


def move_up_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    (
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i0],
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i1],
    ) = (
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i1],
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) < 2:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if (
        index
        == len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets) - 1
    ):
        return
    i0 = index
    i1 = index + 1
    (
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i0],
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i1],
    ) = (
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i1],
        app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()

def advanced_merge_options_bathymetry_dataset(*args):
    toolbox_name = "modelmaker_sfincs_hmt"

    path = os.path.join(app.main_path, "toolboxes", toolbox_name, "config")
    pop_win_config_path  = os.path.join(path, "bathymetry_merge.yml")
    okay, data = app.gui.popup(pop_win_config_path , None)
    if not okay:
        return    


def edit_zmax_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[index][
        "zmax"
    ] = args[0]


def edit_zmin_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[index][
        "zmin"
    ] = args[0]


def edit_offset_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[index][
        "offset"
    ] = args[0]


def edit_buffer_cells_bathymetry_dataset(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "bathymetry_dataset_buffer_cells", args[0])

    subgrid_buffer_cells = app.gui.getvar(
        "modelmaker_sfincs_hmt", "nr_subgrid_pixels"
    ) * app.gui.getvar("modelmaker_sfincs_hmt", "bathymetry_dataset_buffer_cells")
    app.gui.setvar(
        "modelmaker_sfincs_hmt", "subgrid_buffer_cells", subgrid_buffer_cells
    )


def select_interp_method(*args):
    app.gui.setvar("modelmaker_sfincs_hmt", "bathymetry_dataset_interp_method", args[0])


def update():
    group = "modelmaker_sfincs_hmt"
    selected_names = []
    nrd = len(app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets)
    if nrd > 0:
        for dataset in app.toolbox[
            "modelmaker_sfincs_hmt"
        ].selected_bathymetry_datasets:
            selected_names.append(dataset["elevtn"])
        app.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[
            index
        ]
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
        app.gui.setvar(group, "selected_bathymetry_dataset_offset", dataset["offset"])
    else:
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_offset", 0.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)

def generate_bathymetry(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_bathymetry()
