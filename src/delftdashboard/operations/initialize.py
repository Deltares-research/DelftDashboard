"""Application initialization for DelftDashboard.

Reads configuration files (.cfg, .pth, .ini), creates the GUI object,
sets up bathymetry/meteo/tide databases, initializes all registered
models and toolboxes, and builds the GUI layout.
"""

import importlib
import os
import sys
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


def _ask_data_folder() -> str:
    """Open a native folder dialog to select the DelftDashboard data folder.

    Creates a QApplication if one doesn't exist yet. Guitares will
    reuse the same instance later.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QFileDialog

    if QApplication.instance() is None:
        QApplication([])

    dlg = QFileDialog()
    dlg.setWindowTitle(
        "Welcome! Select the DelftDashboard folder. This is the folder where bathymetry, tide models, and other data will be stored."
    )
    dlg.setFileMode(QFileDialog.FileMode.Directory)
    dlg.setOption(QFileDialog.Option.ShowDirsOnly, True)
    dlg.setDirectory(os.path.expanduser("~"))
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowStaysOnTopHint)

    if dlg.exec():
        folders = dlg.selectedFiles()
        return folders[0] if folders else ""
    return ""


def _is_compiled() -> bool:
    """Return True when running as a frozen/compiled binary rather than source.

    Detects a Nuitka standalone build (which injects a ``__compiled__`` global
    into every compiled module) as well as a PyInstaller build (``sys.frozen``).
    """
    return "__compiled__" in globals() or bool(getattr(sys, "frozen", False))


def _last_working_directory_file() -> str:
    """Path of the file that remembers the last-used working directory."""
    return os.path.join(app.config["delft_dashboard_path"], "last_working_directory.txt")


def read_last_working_directory() -> str:
    """Return the remembered last working directory, or "" if there is none."""
    fname = _last_working_directory_file()
    if os.path.exists(fname):
        try:
            with open(fname, "r") as f:
                return f.readline().strip()
        except OSError:
            return ""
    return ""


def save_working_directory(path: str) -> None:
    """Remember *path* as the last-used working directory for the next startup."""
    try:
        with open(_last_working_directory_file(), "w") as f:
            f.write(path + "\n")
    except OSError:
        pass


def initialize_working_directory() -> None:
    """Set the working directory where model input files are written.

    When DelftDashboard is launched *directly* (the current directory is the
    executable's own directory - e.g. a double-click or a Start-menu shortcut),
    change to the remembered last working directory, or to a default
    ``working_directory`` folder inside the DelftDashboard folder (next to
    ``data`` and ``server``) if there is none. When it is launched from another
    directory (running from source, or started from a project folder on the
    command line), that directory is respected and simply remembered for next
    time.
    """
    def _same_dir(a: str, b: str) -> bool:
        # realpath also expands Windows 8.3 short names (the frozen exe often
        # sees short paths, the console long ones - a plain compare misfires)
        try:
            return os.path.normcase(os.path.realpath(a)) == os.path.normcase(
                os.path.realpath(b)
            )
        except OSError:
            return os.path.normcase(os.path.abspath(a)) == os.path.normcase(
                os.path.abspath(b)
            )

    launch_dir = os.path.abspath(os.getcwd())

    # "Launched directly" only applies to a frozen build started from its own
    # (bin) directory; from source we always respect the current directory.
    exe_dir = None
    if _is_compiled():
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    launched_directly = exe_dir is not None and _same_dir(launch_dir, exe_dir)

    if not launched_directly:
        save_working_directory(launch_dir)
        return

    workdir = read_last_working_directory()
    # Never adopt the executable's own folder as working directory (a stale
    # remembered value from before the 8.3 short-path fix could contain it).
    if (
        not workdir
        or not os.path.isdir(workdir)
        or _same_dir(workdir, exe_dir)
    ):
        workdir = os.path.join(app.config["delft_dashboard_path"], "working_directory")
    os.makedirs(workdir, exist_ok=True)
    os.chdir(workdir)
    save_working_directory(workdir)
    print(f"Working directory: {workdir}")


def initialize() -> None:
    """Run the full DelftDashboard initialization sequence.

    Read configuration from ``.cfg``, ``.pth``, and ``.ini`` files, create the
    GUI object, set up bathymetry/meteo/tide databases, initialize all
    toolboxes and models, and assemble the GUI configuration.
    """
    # Note: app.server_path is set later, once the DelftDashboard data folder
    # (from delftdashboard.pth) is known - see below.
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

    # Determine the DelftDashboard folder (which holds the data, server folder,
    # ini file, etc.).
    if _is_compiled():
        # Frozen / Nuitka build. Resolve the DelftDashboard folder (which holds
        # data/, server/ and delftdashboard.ini) in priority order:
        #   1. DELFTDASHBOARD_DATA environment variable (explicit override).
        #   2. A delftdashboard.pth pointer file next to the executable
        #      (written by the installer from the user's chosen location).
        #   3. The per-user application-data folder (default fallback).
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        pth = os.environ.get("DELFTDASHBOARD_DATA", "").strip()
        if not pth:
            pointer_file = os.path.join(exe_dir, "delftdashboard.pth")
            if os.path.exists(pointer_file):
                with open(pointer_file, "r") as f:
                    pth = f.readline().strip()
        if not pth:
            base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            pth = os.path.join(base, "DelftDashboard")
        print(f"Compiled build detected. DelftDashboard folder: {pth}")
    else:
        # Source build: read the delftdashboard.pth file, which contains the
        # path to the DelftDashboard folder.
        # Check working directory first, then package directory
        pth_file_name = os.path.join(os.getcwd(), "delftdashboard.pth")
        if not os.path.exists(pth_file_name):
            pth_file_name = os.path.join(app.main_path, "delftdashboard.pth")
        if not os.path.exists(pth_file_name):
            # Ask the user to select a data folder via a native dialog
            print("No delftdashboard.pth file found. Opening folder dialog...")
            pth = _ask_data_folder()
            if not pth:
                print("No data folder selected. Exiting.")
                raise SystemExit("No data folder selected. Exiting.")
            # Write pth file in the source directory of delftdashboard, so it can be found next time
            pth_file_name = os.path.join(app.main_path, "delftdashboard.pth")
            with open(pth_file_name, "w") as f:
                f.write(pth)
        with open(pth_file_name, "r") as f:
            pth = f.readline().strip()
    app.config["delft_dashboard_path"] = pth
    app.config["data_path"] = os.path.join(app.config["delft_dashboard_path"], "data")

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

    # Remote data store (S3 or S3-compatible). setdefault so all three can
    # be overridden in delftdashboard.ini. To switch back to the old AWS
    # bucket, put this in delftdashboard.ini:
    #   s3_bucket=deltares-ddb
    #   s3_endpoint=
    # (an empty endpoint means AWS S3; s3_region is only used for AWS URLs)
    app.config.setdefault("s3_bucket", "delftdashboard")
    app.config.setdefault("s3_endpoint", "https://s3.deltares.nl")
    app.config.setdefault("s3_region", "eu-west-1")

    # If it does not exist, create it
    if not os.path.exists(app.config["data_path"]):
        os.mkdir(app.config["data_path"])

    # Map server folder. At startup guitares copies its map-engine assets here
    # (see copy_map_server_folder below), and overlays are written here at
    # runtime, so this location must be writable. Place it inside the
    # DelftDashboard folder (the path from delftdashboard.pth), e.g.
    # c:\work\delftdashboard\server, rather than the package source directory,
    # so it also works for a read-only / frozen (Nuitka/PyInstaller) install.
    app.server_path = os.path.join(app.config["delft_dashboard_path"], "server")

    # Set the working directory for model input/output (see function docstring).
    initialize_working_directory()

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

    # Documentation URLs (local Sphinx build)
    # app.main_path = .../DelftDashboard/src/delftdashboard/
    docs_base = os.path.join(
        os.path.dirname(os.path.dirname(app.main_path)),
        "docs", "build", "html",
    )
    # Convert to file:/// URL
    docs_base_url = "file:///" + docs_base.replace("\\", "/")
    app.info.urls = {
        # Models
        "sfincs_hmt": f"{docs_base_url}/models/sfincs_hmt.html",
        "hurrywave_hmt": f"{docs_base_url}/models/hurrywave_hmt.html",
        "delft3dfm": f"{docs_base_url}/models/delft3dfm.html",
        # Toolboxes
        "modelmaker_sfincs_hmt": f"{docs_base_url}/toolboxes/modelmaker_sfincs_hmt.html",
        "modelmaker_hurrywave_hmt": f"{docs_base_url}/toolboxes/modelmaker_hurrywave_hmt.html",
        "modelmaker_delft3dfm": f"{docs_base_url}/toolboxes/modelmaker_delft3dfm.html",
        "bathymetry": f"{docs_base_url}/toolboxes/bathymetry.html",
        "drawing": f"{docs_base_url}/toolboxes/drawing.html",
        "flood_map": f"{docs_base_url}/toolboxes/flood_map.html",
        "nesting": f"{docs_base_url}/toolboxes/nesting.html",
        "observation_stations": f"{docs_base_url}/toolboxes/observation_stations.html",
        "tide_stations": f"{docs_base_url}/toolboxes/tide_stations.html",
        "meteo": f"{docs_base_url}/toolboxes/meteo.html",
        "tropical_cyclone": f"{docs_base_url}/toolboxes/tropical_cyclone.html",
        "tiling": f"{docs_base_url}/toolboxes/tiling.html",
        "watersheds": f"{docs_base_url}/toolboxes/watersheds.html",
        "model_database": f"{docs_base_url}/toolboxes/model_database.html",
        # General
        "index": f"{docs_base_url}/index.html",
        "getting_started": f"{docs_base_url}/getting_started.html",
        "installation": f"{docs_base_url}/installation.html",
        "data_catalogs": f"{docs_base_url}/data_catalogs.html",
    }

    # Check for internet connection
    app.online = True
    try:
        requests.get("http://www.google.com", timeout=5)
    except requests.ConnectionError:
        print("No internet connection available. Cannot check online databases!")
        app.online = False

    # Topography/bathymetry data catalog
    initialize_topography()

    # 3D terrain sources for the map terrain control
    from delftdashboard.operations.s3_store import s3_http_url

    app.terrain_sources = [
        {
            "id": "gebco_2024",
            "name": "GEBCO 2024",
            "tiles": [
                s3_http_url("data/bathymetry/gebco_2024/{z}/{x}/{y}.png")
            ],
            "encoding": "terrarium",
            "tileSize": 256,
            "maxzoom": 8,
        },
    ]

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
        s3_endpoint=app.config.get("s3_endpoint") or None,
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
    app.gui.setvar(
        "view_settings", "topography_dataset", app.background_topography_name
    )
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
    app.gui.setvar("menu", "active_topography_name", app.background_topography_name)

    # Make datashader reuse its compiled aggregations across calls (broken in
    # the frozen build), then warm up the JIT compiles in the background so the
    # warmed results land in the patched cache.
    _patch_datashader_compile_cache()

    # Warm up numba JIT in background (xugrid snap_to_grid etc.)
    # This call can be removed after the numba cell tree teams updates their code
    _warmup_numba()

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

    # Add tiled datasets available on the DDB S3 bucket that are not yet in the
    # local database (mirrors the tide-models / cyclone-tracks auto-update).
    # On a fresh data folder this bootstraps the bathymetry database; tiles are
    # downloaded on demand by the slippy_tile driver.
    if app.online:
        try:
            app.topography_data_catalog.update_from_s3(
                app.config.get("s3_bucket", "deltares-ddb")
            )
        except Exception as e:
            print(f"Could not update bathymetry database from S3: {e}")

    # Selected datasets (list of dicts: {"name": ..., "zmin": ..., "zmax": ...})
    app.selected_bathymetry_datasets = []

    # Populate GUI variables for the bathy/topo selector
    source_names, _ = app.topography_data_catalog.sources()
    if source_names:
        dataset_names, _, _ = app.topography_data_catalog.dataset_names(
            source=source_names[0]
        )
        active_source = source_names[0]
    else:
        # Fresh / empty bathymetry database (no data_catalog.yml yet). Start with
        # an empty selector instead of crashing; background topography stays
        # unavailable until the bathymetry database is populated.
        print(
            f"Warning: no bathymetry datasets found in {path}. "
            "Background topography is unavailable until the bathymetry database "
            "is populated (point DELFTDASHBOARD_DATA at a folder that has one, "
            "or add data\\bathymetry\\data_catalog.yml)."
        )
        dataset_names = []
        active_source = ""
    group = "bathy_topo_selector"
    app.gui.setvar(group, "names", [])
    app.gui.setvar(group, "zmin", [])
    app.gui.setvar(group, "bathymetry_source_names", source_names)
    app.gui.setvar(group, "active_bathymetry_source", active_source)
    app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
    app.gui.setvar(group, "bathymetry_dataset_index", 0)
    app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
    app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
    app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
    app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", 0)

    # Default background topography — ``background_topography_name`` is
    # the catalog source name (str); ``background_topography`` is the
    # actual DataArray for the currently-visible tile, set by
    # ``update_background_topography_data`` after the first successful
    # fetch. They are split so the hover handler can safely test for a
    # loaded DataArray without confusing it with the startup name.
    if "default_bathymetry_dataset" in app.config:
        app.background_topography_name = app.config["default_bathymetry_dataset"]
    else:
        all_names, _, _ = app.topography_data_catalog.dataset_names()
        if "gebco_2024" in all_names:
            app.background_topography_name = "gebco_2024"
        else:
            app.background_topography_name = all_names[0] if all_names else None
    app.background_topography = None


def initialize_toolboxes() -> None:
    """Import and initialize all toolboxes listed in the application config.

    Each toolbox is dynamically imported, instantiated, and has its callback
    module resolved. Toolboxes that fail to initialize are dropped with a
    warning.

    After loading built-in toolboxes, external toolboxes registered via
    the ``delftdashboard.toolboxes`` entry point group are discovered and
    loaded automatically.
    """
    from importlib.metadata import entry_points

    app.toolbox = {}

    # --- Built-in toolboxes (from delftdashboard.cfg) ---
    for tlb in app.config["toolbox"]:
        try:
            toolbox_name = tlb["name"]
            print(f"Adding toolbox : {toolbox_name}")
            module = importlib.import_module(
                f"delftdashboard.toolboxes.{toolbox_name}.{toolbox_name}"
            )
            app.toolbox[toolbox_name] = module.Toolbox(toolbox_name)
            if app.toolbox[toolbox_name].callback_module_name is None:
                app.toolbox[toolbox_name].callback_module = module
            else:
                app.toolbox[toolbox_name].callback_module = importlib.import_module(
                    f"delftdashboard.toolboxes.{toolbox_name}.{app.toolbox[toolbox_name].callback_module_name}"
                )
            app.toolbox[toolbox_name].initialize()

        except Exception as e:
            print(e)
            print(f"Error initializing toolbox {toolbox_name}.")
            if toolbox_name in app.toolbox:
                del app.toolbox[toolbox_name]

    # --- External toolboxes (discovered via entry points) ---
    for ep in entry_points(group="delftdashboard.toolboxes"):
        name = ep.name
        if name in app.toolbox:
            continue  # built-in takes precedence
        try:
            print(f"Adding external toolbox : {name}")
            pkg = ep.load()  # imports the package (e.g. "tsunami")
            module = importlib.import_module(f"{ep.value}.{name}")
            app.toolbox[name] = module.Toolbox(name)
            app.toolbox[name]._external_package = ep.value
            if app.toolbox[name].callback_module_name is None:
                app.toolbox[name].callback_module = module
            else:
                app.toolbox[name].callback_module = importlib.import_module(
                    f"{ep.value}.{app.toolbox[name].callback_module_name}"
                )
            app.toolbox[name].initialize()
        except Exception as e:
            print(e)
            print(f"Error loading external toolbox {name}.")
            if name in app.toolbox:
                del app.toolbox[name]


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
        # Also add external toolboxes (no for_model restriction)
        for toolbox_name in app.toolbox:
            if hasattr(app.toolbox[toolbox_name], "_external_package"):
                if toolbox_name not in app.model[model_name].toolbox:
                    app.model[model_name].toolbox.append(toolbox_name)
        app.model[model_name].initialize()


def _patch_datashader_compile_cache() -> None:
    """Give datashader's compile_components a content-keyed cache.

    Datashader memoizes its (numba-jitted) aggregation pipeline with
    ``toolz.memoize``, keyed on the hash of the reduction/glyph objects. In the
    frozen (Nuitka) build that cache misses on every call, so every render
    re-compiles the numba aggregation - which made e.g. every mask update take
    a long time instead of only the first one. This wraps compile_components
    with a cache keyed on the *content* of the arguments (via datashader's own
    ``_hashable_inputs``), which is stable in both source and frozen builds.
    The original memoized function is still called on a miss, so behaviour is
    unchanged - results are simply reused across calls.
    """
    try:
        import datashader.compiler as _dsc

        if getattr(_dsc.compile_components, "_ddb_stable_cache", False):
            return  # already patched

        _orig = _dsc.compile_components
        _cache: dict = {}

        def _content_key(obj):
            hashable_inputs = getattr(obj, "_hashable_inputs", None)
            if callable(hashable_inputs):
                try:
                    return (type(obj).__qualname__, hashable_inputs())
                except Exception:
                    pass
            return repr(obj)

        def _stable_compile_components(
            agg, schema, glyph, *, antialias=False, cuda=False, partitioned=False
        ):
            key = (
                _content_key(agg),
                str(schema),
                _content_key(glyph),
                antialias,
                cuda,
                partitioned,
            )
            try:
                if key not in _cache:
                    _cache[key] = _orig(
                        agg,
                        schema,
                        glyph,
                        antialias=antialias,
                        cuda=cuda,
                        partitioned=partitioned,
                    )
                return _cache[key]
            except TypeError:
                # Unhashable key component - fall back to the original call.
                return _orig(
                    agg,
                    schema,
                    glyph,
                    antialias=antialias,
                    cuda=cuda,
                    partitioned=partitioned,
                )

        _stable_compile_components._ddb_stable_cache = True
        _dsc.compile_components = _stable_compile_components

        # The data-library modules import compile_components by name, so their
        # module-level references must be patched as well.
        for mod_name in (
            "datashader.data_libraries.pandas",
            "datashader.data_libraries.xarray",
            "datashader.data_libraries.dask",
            "datashader.data_libraries.dask_xarray",
        ):
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "compile_components"):
                    mod.compile_components = _stable_compile_components
            except Exception:
                pass
    except Exception as e:
        print(f"Datashader compile-cache patch failed (non-critical): {e}")


def _warmup_numba() -> None:
    """Trigger numba JIT compilation for xugrid in a background thread.

    The first call to xugrid's ``snap_to_grid`` / ``burn_vector_geometry``
    compiles several numba functions which takes tens of seconds. By running
    tiny dummy calls during startup, the compilation happens in the background
    while the user sees the splash screen, so the first real grid/mask
    operation is not blocked. ``burn_vector_geometry`` (via numba_celltree) is
    what the active-cell mask update uses to rasterise include/exclude polygons;
    without this warmup its first call would compile mid-operation.
    """
    import threading

    def _warmup():
        try:
            import geopandas as gpd
            import numpy as np
            import pandas as pd
            import xarray as xr
            import xugrid as xu
            from shapely.geometry import LineString, Polygon

            # Minimal 2x2 unstructured grid used for the xugrid warmups.
            vertices = np.array(
                [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1]], dtype=float
            )
            faces = np.array([[0, 1, 4, 3], [1, 2, 5, 4]])
            grid = xu.Ugrid2d(vertices[:, 0], vertices[:, 1], -1, faces)

            # 1) snap_to_grid - used when snapping boundary polylines to the grid.
            line = gpd.GeoDataFrame(
                {"geometry": [LineString([(0.5, 0), (0.5, 1)])]},
            )
            xu.snap_to_grid(line, grid, max_snap_distance=0.5)

            # 1b) grid connectivity - numba kernels behind exterior_edges /
            #     edge_node_connectivity, used by model.region (e.g. the
            #     domain check when drawing urban drainage areas).
            _ = grid.edge_node_connectivity
            _ = grid.exterior_edges

            # 2) burn_vector_geometry - used to rasterise include/exclude polygons
            #    when updating the active-cell mask (compiles numba_celltree).
            uda = xu.UgridDataArray(
                xr.DataArray(np.zeros(2), dims=[grid.face_dimension]), grid
            )
            poly = gpd.GeoDataFrame(
                {
                    "geometry": [
                        Polygon([(0.2, 0.2), (1.8, 0.2), (1.8, 0.8), (0.2, 0.8)])
                    ]
                }
            )
            xu.burn_vector_geometry(poly, uda, fill=0, all_touched=False)

            # 3) Datashader map-overlay aggregations. Each JIT-compiles a
            #    different numba aggregation on first use, so all three map
            #    overlays are warmed here:
            #      cvs.line    -> grid / mesh-edge overlay
            #      cvs.points  -> active-cell mask overlay
            #      cvs.trimesh -> elevation overlay
            #    Without this, the first render of each freezes mid-operation in
            #    a frozen build (numba compiling on the GUI thread).
            import datashader as ds
            import datashader.transfer_functions as tf
            from datashader import Canvas

            cvs = Canvas(x_range=[0, 1], y_range=[0, 1], plot_height=16, plot_width=16)
            cvs.line(
                pd.DataFrame({"x1": [0.0], "x2": [1.0], "y1": [0.0], "y2": [1.0]}),
                x=["x1", "x2"],
                y=["y1", "y2"],
                axis=1,
            )
            # NOTE: tf.spread is intentionally NOT warmed up (and no longer
            # used by the mask overlays): its numba kernel is compiled per
            # marker size and takes minutes in a frozen build. The overlays
            # use a scipy binary dilation instead (see hydromt_sfincs /
            # hydromt_hurrywave workflows.map_overlay._dilate_bool_agg).
            pts = pd.DataFrame({"x": [0.1, 0.5, 0.9], "y": [0.1, 0.5, 0.9]})
            tf.shade(
                cvs.points(pts, "x", "y", ds.any()),
                cmap=["#000000", "#ffffff"],
            )
            verts = pd.DataFrame(
                {
                    "x": [0.0, 1.0, 0.0, 1.0],
                    "y": [0.0, 0.0, 1.0, 1.0],
                    "z": [0.0, 1.0, 1.0, 2.0],
                }
            )
            tris = pd.DataFrame({"v0": [0, 1], "v1": [1, 2], "v2": [2, 3]})
            tf.shade(
                cvs.trimesh(
                    verts, tris, mesh=ds.utils.mesh(verts, tris), agg=ds.mean("z")
                ),
                cmap=["#000000", "#ffffff"],
            )

            print("Numba JIT warmup complete.")
        except Exception as e:
            print(f"Numba warmup failed (non-critical): {e}")

    t = threading.Thread(target=_warmup, daemon=True)
    t.start()
