"""Application initialization for DelftDashboard.

Reads configuration files (.cfg, .pth, .ini), creates the GUI object,
sets up bathymetry/meteo/tide databases, initializes all registered
models and toolboxes, and builds the GUI layout.
"""

import importlib
import os
import warnings

# Pre-import pydantic before PySide6/Shiboken is loaded.
# Shiboken hooks into inspect.getsource which interferes with pydantic's
# lazy import mechanism and causes a circular import in pydantic._internal._validators.
import requests
import yaml
from cht_meteo import MeteoDatabase
from cht_tide import TideModelDatabase
from guitares.colormap import read_color_maps
from guitares.gui import GUI
from pyproj import CRS

from delftdashboard.app import app
from delftdashboard.operations.gui import build_gui_config
from delftdashboard.operations.topography import TopographyDataCatalog

warnings.filterwarnings("ignore", message="All-NaN slice encountered")


def initialize() -> None:
    """Run the full DelftDashboard initialization sequence.

    Read configuration from ``.cfg``, ``.pth``, and ``.ini`` files, create the
    GUI object, set up bathymetry/meteo/tide databases, initialize all
    toolboxes and models, and assemble the GUI configuration.
    """
    app.server_path = os.path.join(app.main_path, "server")
    app.config_path = os.path.join(app.main_path, "config")

    # Set default config
    app.config = {}
    app.config["gui_framework"] = "pyqt5"
    app.config["server_port"] = 3000
    app.config["server_nodejs"] = False
    app.config["stylesheet"] = ""
    app.config["map_engine"] = "mapbox"
    app.config["title"] = "Delft Dashboard"
    app.config["width"] = 800
    app.config["height"] = 600
    app.config["model"] = []
    app.config["toolbox"] = []
    app.config["window_icon"] = os.path.join(
        app.config_path, "images", "deltares_icon.png"
    )
    app.config["splash_file"] = os.path.join(
        app.config_path, "images", "DelftDashBoard_python.jpg"
    )
    app.config["bathymetry_database"] = ""
    app.config["sfincs_exe_path"] = ""
    app.config["hurrywave_exe_path"] = ""
    app.config["auto_update_bathymetry"] = True
    app.config["auto_update_tide_models"] = True

    # Read cfg file and override stuff in default config dict
    # cfg file contains gui config stuff, but not properties that need to be
    # edited by the user! It always sits in the config folder.
    # Note that values in the keyword-value pairs in the cfg file will be
    # overwritten with values in the ini file if they are present there!
    cfg_file_name = os.path.join(app.config_path, "delftdashboard.cfg")
    cfgfile = open(cfg_file_name, "r")
    config = yaml.load(cfgfile, Loader=yaml.FullLoader)
    for key in config:
        app.config[key] = config[key]
    cfgfile.close()

    # First read delftdashboard.pth file. This contains the path to the
    # delftdashboard folder.
    pth_file_name = os.path.join(app.main_path, "delftdashboard.pth")
    # Check if pth file exist. If not, give error message and exit
    if not os.path.exists(pth_file_name):
        # Ask the user to enter a path to the delftdashboard folder
        print(
            f"Cannot find the file {pth_file_name} which contains the name of the Delft Dashboard folder where the data will be stored."
        )
        print(
            r"Please enter a path to the Delft Dashboard folder (e.g. c:\work\delftdashboard):"
        )
        pth = input()
        pthfile = open(pth_file_name, "w")
        pthfile.write(pth)
        pthfile.close()
    pthfile = open(pth_file_name, "r")
    pth = pthfile.readline().strip()
    app.config["delft_dashboard_path"] = pth
    app.config["data_path"] = os.path.join(app.config["delft_dashboard_path"], "data")
    pthfile.close()

    # Now check if the ini file exists. If not, give warning and create it.
    ini_file_name = os.path.join(
        app.config["delft_dashboard_path"], "delftdashboard.ini"
    )
    if not os.path.exists(ini_file_name):
        print(
            f"The ini file {ini_file_name} does not exist. It will be created but you'll need to edit it."
        )
        inifile = open(ini_file_name, "w")
        inifile.write(
            "# This file need to be copied to delftdashboard.ini and edited. Please do NOT edit and push this file itself.\n"
        )
        inifile.write(
            "# Please enter correct Delft Dashboard data path (where the bathymetry and tide models etc are store) and model executable folders.\n"
        )
        inifile.write("sfincs_exe_path: c:\\programs\\sfincs\n")
        inifile.write("hurrywave_exe_path: c:\\programs\\hurrywave\n")
        inifile.write("auto_update_bathymetry: true\n")
        inifile.write("auto_update_tide_models: true\n")
        inifile.close()

    # Read ini file and override stuff in default config dict
    # ini file contains properties that need to be edited by the user!
    # Note that values in the keyword-value pairs in the cfg file will be
    # overwritten with values in the ini file if they are present!
    inifile = open(ini_file_name, "r")
    config = yaml.load(inifile, Loader=yaml.FullLoader)
    for key in config:
        app.config[key] = config[key]
    inifile.close()

    # First we check if the folder pth exists. If not, give warning and create it.
    if not os.path.exists(app.config["delft_dashboard_path"]):
        print("The folder specified in delftdashboard.pth does not exist. Creating it.")
        os.mkdir(app.config["delft_dashboard_path"])

    # The data path always sits in the delftdashboard folder
    app.config["data_path"] = os.path.join(app.config["delft_dashboard_path"], "data")

    # Set S3 bucket name
    app.config["s3_bucket"] = "deltares-ddb"

    # If it does not exist, create it
    if not os.path.exists(app.config["data_path"]):
        os.mkdir(app.config["data_path"])

    # Initialize GUI object
    app.gui = GUI(
        app,
        framework=app.config["gui_framework"],
        config_path=app.config_path,
        server_path=app.server_path,
        server_nodejs=app.config["server_nodejs"],
        server_port=app.config["server_port"],
        stylesheet=app.config["stylesheet"],
        icon=app.config["window_icon"],
        splash_file=app.config["splash_file"],
        map_engine=app.config["map_engine"],
        copy_map_server_folder=True,
    )

    # Check for internet connection
    app.online = True
    try:
        requests.get("http://www.google.com", timeout=5)
    except requests.ConnectionError:
        print("No internet connection available. Cannot check online databases!")
        app.online = False

    # Topography/bathymetry data catalog
    initialize_topography()

    # Define some other variables
    app.crs = CRS(4326)

    # Meteo database
    if "meteo_database_path" not in app.config:
        app.config["meteo_database_path"] = os.path.join(
            app.config["data_path"], "meteo_database"
        )
    s3_bucket = app.config["s3_bucket"]
    s3_key = "data/meteo"
    app.meteo_database = MeteoDatabase(path=app.config["meteo_database_path"])
    app.meteo_database.read_datasets()

    # Tide model database
    if "tide_model_database_path" not in app.config:
        app.config["tide_model_database_path"] = os.path.join(
            app.config["data_path"], "tide_models"
        )
    s3_bucket = app.config["s3_bucket"]
    s3_key = "data/tide_models"
    app.tide_model_database = TideModelDatabase(
        path=app.config["tide_model_database_path"],
        s3_bucket=s3_bucket,
        s3_key=s3_key,
        check_online=app.online,
    )
    short_names, long_names = app.tide_model_database.dataset_names()
    app.gui.setvar("tide_models", "long_names", long_names)
    app.gui.setvar("tide_models", "names", short_names)

    # Model database
    if "model_database_path" not in app.config:
        app.config["model_database_path"] = os.path.join(
            app.config["data_path"], "model_database"
        )
        # Initializing will happen when the model database toolbox is selected

    # Use GUI variables to set the view settings

    # Layer style
    if app.gui.map_engine == "mapbox":
        app.gui.setvar("view_settings", "layer_style", "streets-v12")
    else:
        app.gui.setvar("view_settings", "layer_style", "osm")
    # Projection
    app.gui.setvar("view_settings", "projection", "mercator")
    # Topography
    app.gui.setvar("view_settings", "topography_dataset", app.background_topography)
    app.gui.setvar("view_settings", "topography_auto_update", "True")
    app.gui.setvar("view_settings", "topography_visible", True)
    app.gui.setvar("view_settings", "topography_colormap", "earth")
    app.gui.setvar("view_settings", "topography_autoscaling", True)
    app.gui.setvar("view_settings", "topography_opacity", 0.7)
    app.gui.setvar("view_settings", "topography_quality", "high")
    app.gui.setvar("view_settings", "topography_hillshading", True)
    app.gui.setvar("view_settings", "topography_interp_method", "linear")
    app.gui.setvar("view_settings", "topography_zmin", -10.0)
    app.gui.setvar("view_settings", "topography_zmax", 10.0)
    app.gui.setvar("view_settings", "layer_style", "streets-v12")
    app.gui.setvar("view_settings", "terrain_exaggeration", 1.5)
    app.gui.setvar("view_settings", "terrain_visible", False)
    # Read color maps (should be done in guitares)
    cmps = read_color_maps(os.path.join(app.config_path, "colormaps"))
    app.gui.setvar("view_settings", "colormaps", cmps)

    # Initialize toolboxes
    initialize_toolboxes()

    # Initialize models
    initialize_models()

    # Set active toolbox and model
    app.active_model = app.model[list(app.model)[0]]
    app.active_toolbox = app.toolbox[list(app.toolbox)[0]]

    # GUI variables
    app.gui.setvar("menu", "active_model_name", "")
    app.gui.setvar("menu", "active_toolbox_name", "")
    app.gui.setvar("menu", "active_topography_name", app.background_topography)

    # Now build up GUI config
    build_gui_config()


def initialize_topography() -> None:
    """Load the topography/bathymetry data catalog and set up GUI variables."""
    if "bathymetry_database_path" not in app.config:
        app.config["bathymetry_database_path"] = os.path.join(
            app.config["data_path"], "bathymetry"
        )
    path = app.config["bathymetry_database_path"]

    app.topography_data_catalog = TopographyDataCatalog(path)
    # Backward-compatible alias for toolboxes that still use cht_bathymetry
    app.bathymetry_database = app.topography_data_catalog

    # Selected datasets (list of dicts: {"name": ..., "zmin": ..., "zmax": ...})
    app.selected_bathymetry_datasets = []

    # Populate GUI variables for the bathy/topo selector
    source_names, _ = app.topography_data_catalog.sources()
    dataset_names, _, _ = app.topography_data_catalog.dataset_names(
        source=source_names[0]
    )
    group = "bathy_topo_selector"
    app.gui.setvar(group, "names", [])
    app.gui.setvar(group, "zmin", [])
    app.gui.setvar(group, "bathymetry_source_names", source_names)
    app.gui.setvar(group, "active_bathymetry_source", source_names[0])
    app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
    app.gui.setvar(group, "bathymetry_dataset_index", 0)
    app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
    app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
    app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
    app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

    # Default background topography
    if "default_bathymetry_dataset" in app.config:
        app.background_topography = app.config["default_bathymetry_dataset"]
    else:
        all_names, _, _ = app.topography_data_catalog.dataset_names()
        if "gebco_2024" in all_names:
            app.background_topography = "gebco_2024"
        else:
            app.background_topography = all_names[0] if all_names else None


def initialize_toolboxes() -> None:
    """Import and initialize all toolboxes listed in the application config.

    Each toolbox is dynamically imported, instantiated, and has its callback
    module resolved. Toolboxes that fail to initialize are dropped with a
    warning.
    """
    app.toolbox = {}
    for tlb in app.config["toolbox"]:
        try:
            toolbox_name = tlb["name"]
            # And initialize this toolbox
            print(f"Adding toolbox : {toolbox_name}")
            module = importlib.import_module(
                f"delftdashboard.toolboxes.{toolbox_name}.{toolbox_name}"
            )
            # Initialize the toolbox
            app.toolbox[toolbox_name] = module.Toolbox(toolbox_name)
            # Set the callback module. This is the module that contains the
            # callback functions, and does not have to be the same as the
            # toolbox module. This is useful as some toolboxes do not have
            # tabs for which modules are defined, and the main module can
            # become very busy with all the callbacks and the toolbox object.
            if app.toolbox[toolbox_name].callback_module_name is None:
                # Callback module is same as toolbox module
                app.toolbox[toolbox_name].callback_module = module
            else:
                # Callback module is different from toolbox module
                app.toolbox[toolbox_name].callback_module = importlib.import_module(
                    f"delftdashboard.toolboxes.{toolbox_name}.{app.toolbox[toolbox_name].callback_module_name}"
                )
            app.toolbox[toolbox_name].initialize()

        # Write error message if toolbox cannot be initialized
        except Exception as e:
            print(e)
            print(f"Error initializing toolbox {toolbox_name}.")
            # Drop toolbox from dictionary
            if toolbox_name in app.toolbox:
                del app.toolbox[toolbox_name]


def initialize_models() -> None:
    """Import and initialize all models listed in the application config.

    Each model is dynamically imported, instantiated, and has its compatible
    toolboxes determined from the toolbox config entries.
    """
    app.model = {}
    for mdl in app.config["model"]:
        model_name = mdl["name"]
        # And initialize the domain for this model
        print(f"Adding model   : {model_name}")
        module = importlib.import_module(
            f"delftdashboard.models.{model_name}.{model_name}"
        )
        app.model[model_name] = module.Model(model_name)
        if "exe_path" in mdl:
            app.model[model_name].exe_path = mdl["exe_path"]
        else:
            app.model[model_name].exe_path = ""
        # Loop through toolboxes to see which ones should be activated for
        # which model
        app.model[model_name].toolbox = []
        for tlb in app.config["toolbox"]:
            okay = True
            if "for_model" in tlb:
                if model_name not in tlb["for_model"]:
                    okay = False
            if okay:
                app.model[model_name].toolbox.append(tlb["name"])
        app.model[model_name].initialize()
