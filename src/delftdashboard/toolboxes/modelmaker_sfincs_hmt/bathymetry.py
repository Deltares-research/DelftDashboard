import os
import subprocess
import yaml
import rasterio
from rasterio.enums import Resampling

from hydromt import DataCatalog

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

    if source == "Add your own dataset":
        app.gui.setvar("modelmaker_sfincs_hmt", "add_topobathy_flag", True)
        source = "User"

    list_bathymetry_datasets(source)

def list_bathymetry_datasets(source):
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

    if len(dataset_names) > 0:
        name = dataset_names[0]
        meta = app.data_catalog[name].meta
        meta_str = yaml.dump(meta, default_flow_style=False)
        app.gui.setvar(
            "modelmaker_sfincs_hmt", "selected_bathymetry_dataset_meta", meta_str
        )

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
    pop_win_config_path = os.path.join(path, "bathymetry_info.yml")
    okay, data = app.gui.popup(pop_win_config_path, None)
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

def add_dataset(*args):
    """ Add a dataset to your data_catalog and add to the available datasets in the GUI
    """

    # select file to add
    fn = app.gui.window.dialog_open_file(
        "Select file with topobathy data ...", filter="*.tif"
    )

    if fn[0]:
        # check the file format, it should be a cloud-optimized geotiff with overviews
        # and a nodata value and a valid crs
        with rasterio.open(fn[0], mode="r+") as src:
            if not src.driver == "GTiff":
                app.gui.window.dialog_warning("File is not a GeoTiff")
                return
            if not src.overviews(1):
                ok = app.gui.window.dialog_yes_no(
                    "File does not have overviews (i.e., reduced resolution versions of the dataset)" +
                    "\nYou can create them manually using the command: `rio overview --build auto <your_dataset.tif>" +
                    "\nFor more information see: https://rasterio.readthedocs.io/en/latest/topics/overviews.html" +

                    "\n\nNote that this will edit the file directly and increase its size significantly." +
                    "\nThere is no undo for this, so please make a backup before pressing ok." +
                    "\n\nDo you want to automatically create the overviews?"
                    )
                if not ok:
                    return
                else:
                    try:
                        # create new overviews, resampling with average method
                        src.build_overviews([2, 4, 8, 16, 32, 64], Resampling.average)
                    
                        # update dataset tags
                        src.update_tags(ns='rio_overview', resampling='average')

                        app.gui.window.dialog_info("Overviews created successfully")
                    except Exception as e:
                        app.gui.window.dialog_warning(f"Failed to create overviews: {e}")
                        return
                
            if not src.nodata:
                app.gui.window.dialog_warning("File does not have a nodata value")
                return
            if not src.crs:
                app.gui.window.dialog_warning("File does not have a valid CRS")
                return
            else:
                epsg = src.crs.to_epsg()

        # ask for a name for the dataset
        name, okay = app.gui.window.dialog_string("Provide a name for the dataset", "New dataset")
        if not okay:
            # Cancel was clicked
            return
        # check whether the name already exists in the data catalog
        while name in app.data_catalog.sources.keys():
            name, okay = app.gui.window.dialog_string("Dataset name already exists. Provide a different name", "New dataset")
            if not okay:
                # Cancel was clicked
                return

        # create data catalog entry
        yml_str = f"""
        {name}:
            path: {fn[0]}
            data_type: RasterDataset
            driver: raster
            crs: {epsg}
            meta:
                category: topography
                source: User
        """            

        # check if my_data_catalog.yml exists
        my_data_catalog = os.path.join(app.main_path, "config", "my_data_catalog.yml")
        if not os.path.exists(my_data_catalog):
            with open(my_data_catalog, "w") as f:
                f.write(yml_str)
            
            # add to delft_dashboard.ini
            app.config["data_libs"].append(my_data_catalog)

            inifile = os.path.join(app.main_path, "config", "delftdashboard.ini")
            with open(inifile, "r") as f:
                config = yaml.safe_load(f)

            with open(inifile, "w") as f:
                config["data_libs"] = app.config["data_libs"]
                yaml.dump(config, f)
        else:
            with open(my_data_catalog, "a") as f:
                f.write(yml_str)
        
        # reload the data catalog
        app.data_catalog = DataCatalog(data_libs=app.config["data_libs"])
        list_bathymetry_datasets(source="User")

        # reloading doesnt work yet, so we need to restart the app
        app.gui.window.dialog_warning("Adding your own datasets is beta functionality. To use and view the dataset you just added, restart the app and go to menu -> Topgraphy -> User.")


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
    pop_win_config_path = os.path.join(path, "bathymetry_merge.yml")
    okay, data = app.gui.popup(pop_win_config_path, None)
    if not okay:
        return


def edit_zmax_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[index]["zmax"] = (
        args[0]
    )


def edit_zmin_bathymetry_dataset(*args):
    group = "modelmaker_sfincs_hmt"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox["modelmaker_sfincs_hmt"].selected_bathymetry_datasets[index]["zmin"] = (
        args[0]
    )


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
