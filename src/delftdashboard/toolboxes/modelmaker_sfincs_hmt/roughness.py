from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()
    app.map.layer["sfincs_hmt"].layer["grid"].set_mode("active")


def select_roughness_method(*args):
    pass


def add_selected_manning_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "roughness_methods_index")
    if index == 0:
        manning_sea = app.gui.getvar(group, "manning_sea")
        manning_land = app.gui.getvar(group, "manning_land")
        rgh_lev_land = app.gui.getvar(group, "rgh_lev_land")
        if "Constant values" not in app.gui.getvar(
            group, "selected_manning_dataset_names"
        ):
            dataset = {
                "name": "Constant values",
                "manning_sea": manning_sea,
                "manning_land": manning_land,
                "rgh_lev_land": rgh_lev_land,
            }
            app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets.append(
                dataset
            )
    elif index == 1:
        reclass_table = app.gui.getvar(group, "lulc_reclass_table")
        lulc = app.gui.getvar(group, "lulc_dataset_names")[
            app.gui.getvar(group, "lulc_dataset_index")
        ]
        if lulc not in app.gui.getvar(group, "selected_manning_dataset_names"):
            dataset = {"lulc": lulc, "reclass_table": reclass_table}
            app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets.append(
                dataset
            )
    elif index == 2:
        manning = app.gui.getvar(group, "manning_dataset_names")[
            app.gui.getvar(group, "manning_dataset_index")
        ]
        if manning not in app.gui.getvar(group, "selected_manning_dataset_names"):
            dataset = {"manning": manning}
            app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets.append(
                dataset
            )

    app.gui.setvar(
        group,
        "selected_manning_dataset_index",
        len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets) - 1,
    )
    update()


def remove_selected_manning_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets) == 0:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_manning_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets.pop(index)
    update()


def select_selected_manning_dataset(*args):
    update()


def select_manning_dataset(*args):
    pass


def select_lulc_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "lulc_dataset_index")
    landuse_names = app.gui.getvar(group, "lulc_dataset_names")

    if len(landuse_names) > 0:
        name = landuse_names[index]
        app.gui.setvar(
            "modelmaker_sfincs_hmt", "lulc_reclass_table", f"{name}_mapping.csv"
        )


def select_reclass_table(*args):
    fname = app.gui.window.dialog_open_file(
        "Select mapping file to convert landuse/ladncover to Mannings' n",
        filter="*.csv",
    )
    if fname:
        app.gui.setvar("modelmaker_sfincs_hmt", "lulc_reclass_table", fname)
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[0].update(
            {"reclass_table": fname}
        )


def move_up_selected_manning_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets) < 2:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_manning_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    (
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i0],
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i1],
    ) = (
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i1],
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i0],
    )
    app.gui.setvar(group, "selected_manning_dataset_index", index - 1)
    update()


def move_down_selected_manning_dataset(*args):
    if len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets) < 2:
        return
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_manning_dataset_index")
    if index == len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    (
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i0],
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i1],
    ) = (
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i1],
        app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[i0],
    )
    app.gui.setvar(group, "selected_manning_dataset_index", index + 1)
    update()


def update():
    group = "modelmaker_sfincs_hmt"
    selected_names = []
    nrd = len(app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets)
    if nrd > 0:
        for dataset in app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets:
            if "lulc" in dataset:
                selected_names.append(dataset["lulc"])
            elif "manning" in dataset:
                selected_names.append(dataset["manning"])
            elif "name" in dataset:
                selected_names.append(dataset["name"])
        app.gui.setvar(group, "selected_manning_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_manning_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.toolbox["modelmaker_sfincs_hmt"].selected_manning_datasets[index]
    else:
        app.gui.setvar(group, "selected_manning_dataset_names", [])
        app.gui.setvar(group, "selected_manning_dataset_index", 0)

    app.gui.setvar(group, "nr_selected_manning_datasets", nrd)


def generate_manning(*args):
    app.toolbox["modelmaker_sfincs_hmt"].generate_manning()
