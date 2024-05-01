import geopandas as gpd
import pandas as pd
import time
import copy
from pathlib import Path
from shapely.geometry import Polygon

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map
from delftdashboard.operations.checklist import zoom_to_boundary


class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Model Boundary | Quick Build"

        # Set GUI variable

        group = "modelmaker_fiat"

        app.gui.setvar(group, "selected_aoi_method", "polygon")
        app.gui.setvar(
            group,
            "setup_aoi_method_string",
            ["Draw polygon", "Draw box", "SFINCS model domain", "Upload file"],
        )
        app.gui.setvar(
            group,
            "setup_aoi_method_value",
            ["polygon", "box", "sfincs", "file"],
        )
        app.gui.setvar(group, "active_area_of_interest", "")
        app.gui.setvar(group, "area_of_interest", 0)
        app.gui.setvar(group, "selected_crs", "EPSG:4326")

        # To display the quick build
        app.gui.setvar(group, "show_asset_locations", False)
        app.gui.setvar(group, "show_roads", False)

        ## DEPENDENDY FOR THE TITLES IN THE MODEL BOUNDARY TAB
        app.gui.setvar(group, "titles_model_boundary_tab", 1)

        # Area of Interest
        app.gui.setvar(group, "model_boundary_file_list", [])
        app.gui.setvar(group, "selected_model_boundary", 0)
        app.gui.setvar(group, "area_of_interest_string", "")
        app.gui.setvar(group, "area_of_interest_value", None)
        app.gui.setvar("modelmaker_fiat", "fn_model_boundary_file_list", [])

        self.area_of_interest = gpd.GeoDataFrame()
        self.area_of_interest_file_name = "area_of_interest.geojson"

        self.setup_dict = {}

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["modelmaker_fiat"].hide()
        if mode == "invisible":
            app.map.layer["modelmaker_fiat"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("modelmaker_fiat")

        layer.add_layer(
            "area_of_interest_bbox",
            type="draw",
            shape="rectangle",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_polygon",
            type="draw",
            shape="polygon",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_from_file",
            type="draw",
            shape="polygon",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

        layer.add_layer(
            "area_of_interest_from_sfincs",
            type="draw",
            shape="polygon",
            polygon_line_color="orange",
            polygon_fill_color="#fcc203",
            polygon_fill_opacity=0.3,
            rotate=True,
        )

    def set_crs(self):
        selected_crs = app.gui.getvar("modelmaker_fiat", "selected_crs")
        app.gui.setvar("fiat", "selected_crs", selected_crs)


## CALLBACKS ARE MOVED HERE FROM DOMAIN.PY BECAUSE OTHERWISE IT COULD NOT BE FOUND ##
def select(*args):
    # De-activate existing layers
    map.update()
    # Show the grid outline layer
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer:
        app.map.layer["modelmaker_fiat"].layer[active_layer].set_mode("active")
    app.gui.setvar("_main", "show_fiat_checkbox", True)


def draw_boundary(*args):
    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )
        # Initiate a new FIAT model
        app.active_model.select_working_directory()

        # Load the file
        selected_method = app.gui.getvar("modelmaker_fiat", "selected_aoi_method")
        if selected_method == "polygon":
            draw_polygon()
        elif selected_method == "box":
            draw_bbox()
        elif selected_method == "sfincs":
            app.gui.window.dialog_info(
                "Please select your SFINCS model root folder",
                "Select SFINCS root folder",
            )
            load_sfincs_domain()
        elif selected_method == "file":
            app.gui.window.dialog_info(
                "Please select your model boundary files",
                "Select Model Boundary files",
            )
            load_aoi_file()
    else:
        selected_method = app.gui.getvar("modelmaker_fiat", "selected_aoi_method")
        if selected_method == "polygon":
            draw_polygon()
        elif selected_method == "box":
            draw_bbox()
        elif selected_method == "sfincs":
            load_sfincs_domain()
        elif selected_method == "file":
            load_aoi_file()


def generate_boundary(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer == "":
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )
        return

    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )

        # Initiate a new FIAT model
        app.active_model.select_working_directory()

    gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()
    app.active_toolbox.area_of_interest = gdf.set_crs(app.crs)

    app.active_toolbox.area_of_interest.to_file(
        app.active_model.domain.database.drive / "aoi.geojson", driver="GeoJSON"
    )

    app.active_model.domain.exposure_vm.create_interest_area(
        fpath=str(app.active_model.domain.database.drive / "aoi.geojson")
    )

    app.map.layer["modelmaker_fiat"].layer[active_layer].hide()
    time.sleep(0.5)
    app.map.layer["modelmaker_fiat"].layer[active_layer].show()

    # Check the checkbox
    app.gui.setvar("_main", "checkbox_model_boundary", True)

    # Fly to the site
    zoom_to_boundary()


def select_method(*args):
    app.gui.setvar("modelmaker_fiat", "selected_aoi_method", args[0])


def set_crs(*args):
    app.toolbox["modelmaker_fiat"].set_crs()


def clear_aoi_layers():
    aoi_layers = [
        "area_of_interest_bbox",
        "area_of_interest_polygon",
        "area_of_interest_from_file",
        "area_of_interest_from_sfincs",
    ]
    if app.gui.getvar("modelmaker_fiat", "area_of_interest") == 1:
        for lyr in aoi_layers:
            layer = app.map.layer["modelmaker_fiat"].layer[lyr]
            layer.clear()


def draw_bbox():
    clear_aoi_layers()

    # Clear grid outline layer
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_bbox"].draw()

    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_bbox"
    )


def draw_polygon():
    clear_aoi_layers()

    # Set the crs of the polygon layer and draw it
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer["area_of_interest_polygon"].draw()

    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_polygon"
    )


def write_fn_to_table(*args):
    fn_model_boundary = app.gui.getvar("modelmaker_fiat", "area_of_interest_value")
    name_model_boundary = app.gui.getvar("modelmaker_fiat", "area_of_interest_string")
    list_model_boundaries = app.gui.getvar(
        "modelmaker_fiat", "model_boundary_file_list"
    )
    fn_list_model_boundaries = app.gui.getvar(
        "modelmaker_fiat", "fn_model_boundary_file_list"
    )
    if name_model_boundary not in list_model_boundaries:
        list_model_boundaries.append(name_model_boundary)
    app.gui.setvar("modelmaker_fiat", "model_boundary_file_list", list_model_boundaries)
    if fn_model_boundary not in fn_list_model_boundaries:
        fn_list_model_boundaries.append(fn_model_boundary)
    app.gui.setvar(
        "modelmaker_fiat", "fn_model_boundary_file_list", fn_list_model_boundaries
    )


def set_active_area_file(*args):
    clear_aoi_layers()
    fn_index = app.gui.getvar("modelmaker_fiat", "selected_model_boundary")
    selected_fn_model_boundary = app.gui.getvar(
        "modelmaker_fiat", "fn_model_boundary_file_list"
    )[fn_index]

    gdf = gpd.read_file(selected_fn_model_boundary)
    gdf.to_crs(app.crs, inplace=True)

    # Add the polygon to the map
    layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
    layer.set_data(gdf)
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_file"
    )


def load_aoi_file():
    clear_aoi_layers()
    fname = app.gui.window.dialog_open_file(
        "Select Area of Interest File", filter="*.shp *.geojson *.gpkg"
    )
    if fname[0]:
        app.gui.setvar(
            "modelmaker_fiat", "area_of_interest_string", Path(fname[0]).name
        )
        app.gui.setvar("modelmaker_fiat", "area_of_interest_value", fname[0])
        write_fn_to_table()
        file_list = app.gui.getvar("modelmaker_fiat", "model_boundary_file_list")

        if len(file_list) == 1:
            gdf = gpd.read_file(fname[0])
            gdf.to_crs(app.crs, inplace=True)

            # Add the polygon to the map
            layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
            layer.set_data(gdf)
            app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
            app.gui.setvar(
                "modelmaker_fiat",
                "active_area_of_interest",
                "area_of_interest_from_file",
            )


def load_sfincs_domain(*args):
    clear_aoi_layers()

    fname = app.gui.window.dialog_select_path("Select the SFINCS model folder")
    if fname:
        path_to_sfincs_domain = Path(fname) / "gis" / "region.geojson"
        if path_to_sfincs_domain.exists():
            gdf = gpd.read_file(path_to_sfincs_domain)
            gdf.to_crs(app.crs, inplace=True)


            # Write file into table
            app.gui.setvar(
                "modelmaker_fiat", "area_of_interest_string", path_to_sfincs_domain.name
            )
            app.gui.setvar(
                "modelmaker_fiat", "area_of_interest_value", path_to_sfincs_domain
            )
            write_fn_to_table()

            # Add the polygon to the map
            layer = app.map.layer["modelmaker_fiat"].layer[
                "area_of_interest_from_sfincs"
            ]
            layer.set_data(gdf)

            app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
            app.gui.setvar(
                "modelmaker_fiat",
                "active_area_of_interest",
                "area_of_interest_from_sfincs",
            )

        else:
            app.gui.window.dialog_warning(
                f"The region.geojson file cannot be found in folder {str(Path(fname) / 'gis')}",
                "No region.geojson file found.",
            )
            return


def quick_build(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer == "":
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )
        return

    if app.active_model.domain is None:
        app.gui.window.dialog_warning(
            "Please first select a folder for your FIAT model",
            "No FIAT model initiated yet",
        )

        # Initiate a new FIAT model
        app.active_model.select_working_directory()

    model = "fiat"
    checkbox_group = "_main"

    dlg = app.gui.window.dialog_wait("\nCreating a FIAT model...")
    app.gui.setvar(model, "created_nsi_assets", "nsi")
    app.gui.setvar(model, "text_feedback_create_asset_locations", "NSI assets created")

    crs = app.gui.getvar(model, "selected_crs")

    # BUILDINGS with default settings
    app.active_model.domain.exposure_vm.set_asset_locations_source(
        source="NSI", ground_floor_height="NSI", crs=crs
    )

    # Set the damage curves
    selected_damage_curve_database = "default_vulnerability_curves"
    selected_link_table = "default_hazus_iwr_linking"
    app.gui.setvar(
        model, "selected_damage_curve_database", selected_damage_curve_database
    )
    app.gui.setvar(model, "selected_damage_curve_linking_table", selected_link_table)
    app.active_model.domain.vulnerability_vm.add_vulnerability_curves_to_model(
        selected_damage_curve_database, selected_link_table
    )

    # ROADS with default settings
    # By default it is taking the following road types:
    # "motorway",
    # "motorway_link",
    # "trunk",
    # "trunk_link",
    # "primary",
    # "primary_link",
    # "secondary",
    # "secondary_link",
    app.active_model.domain.exposure_vm.set_roads_settings()

    # Set the road damage threshold
    road_damage_threshold = app.gui.getvar("fiat", "road_damage_threshold")
    app.active_model.domain.vulnerability_vm.set_road_damage_threshold(
        road_damage_threshold
    )

    # Set SVI and equity
    census_key_path = Path(app.config_path) / "census_key.txt"
    if census_key_path.exists():
        fid = open(census_key_path, "r")
        census_key = fid.readlines()
        fid.close()

    census_key = census_key[0]
    year_data = 2021  ## default

    app.active_model.domain.svi_vm.set_svi_settings(census_key, year_data)
    app.active_model.domain.svi_vm.set_equity_settings(census_key, year_data)

    # Set the checkboxes checked
    app.gui.setvar("fiat", "show_roads", True)
    app.gui.setvar("modelmaker_fiat", "show_roads", True)
    app.gui.setvar(model, "show_asset_locations", True)
    app.gui.setvar("modelmaker_fiat", "show_asset_locations", True)
    app.gui.setvar("_main", "checkbox_vulnerability", True)

    app.gui.setvar(checkbox_group, "checkbox_asset_locations", True)
    app.gui.setvar(checkbox_group, "checkbox_classification", True)
    app.gui.setvar(checkbox_group, "checkbox_damage_values", True)
    app.gui.setvar(checkbox_group, "checkbox_finished_floor_height", True)
    app.gui.setvar(checkbox_group, "checkbox_svi_(optional)", True)
    app.gui.setvar("_main", "checkbox_roads_(optional)", True)

    # Set the sources
    app.gui.setvar(model, "source_asset_locations", "National Structure Inventory")
    app.gui.setvar(model, "source_classification", "National Structure Inventory")
    app.gui.setvar(
        model, "source_finished_floor_height", "National Structure Inventory"
    )
    app.gui.setvar(model, "source_max_potential_damage", "National Structure Inventory")
    app.gui.setvar(model, "source_ground_elevation", "National Structure Inventory")

    # Run HydroMT-FIAT and show the model and set the GUI variables
    buildings, roads = app.active_model.domain.run_hydromt_fiat()

    # Set the buildings and roads attribute to gdf for easy visualization
    if buildings is not None:
        app.active_model.buildings = buildings
        app.active_model.buildings.set_crs(crs, inplace=True)
    if roads is not None:
        app.active_model.roads = roads
        app.active_model.roads.set_crs(crs, inplace=True)

    list_types_primary = list(
        app.active_model.buildings["Primary Object Type"].unique()
    )
    list_types_secondary = list(
        app.active_model.buildings["Secondary Object Type"].unique()
    )
    list_types_primary.sort()
    list_types_secondary.sort()
    df = pd.DataFrame(
        data={
            "Secondary Object Type": list_types_secondary,
            "Assigned: Structure": "",
            "Assigned: Content": "",
        }
    )
    ## TODO: add the nr of stories and the basement

    app.gui.setvar(model, "exposure_categories_to_link", df)

    app.map.layer["buildings"].layer["exposure_points"].crs = crs
    app.map.layer["buildings"].layer["exposure_points"].set_data(
        app.active_model.buildings
    )

    # Set the primary and secondary object type lists
    app.active_model.set_object_types(list_types_primary, list_types_secondary)

    # Set the unit for Exposure Data for visualization
    view_tab_unit = app.active_model.domain.fiat_model.exposure.unit
    app.gui.setvar(model, "view_tab_unit", view_tab_unit)

    # Show the roads
    app.map.layer["roads"].layer["exposure_lines"].crs = crs
    app.map.layer["roads"].layer["exposure_lines"].set_data(app.active_model.roads)
    app.active_model.show_exposure_roads()

    dlg.close()

    app.gui.window.dialog_info(
        f"A FIAT model is created in:\n{app.active_model.domain.fiat_model.root}",
        "FIAT model created",
    )


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
        app.map.layer["buildings"].clear()
        app.gui.setvar("fiat", "show_primary_classification", False)
        app.gui.setvar("fiat", "show_secondary_classification", False)
        app.map.layer["buildings"].layer["exposure_points"].crs = crs = app.gui.getvar(
            "fiat", "selected_crs"
        )
        app.map.layer["buildings"].layer["exposure_points"].set_data(
            app.active_model.buildings
        )

        app.active_model.show_exposure_buildings()
    else:
        app.active_model.hide_exposure_buildings()


def display_roads(*args):
    """Show/hide roads layer"""
    app.gui.setvar("fiat", "show_roads", args[0])
    if args[0]:
        app.active_model.show_exposure_roads()
    else:
        app.active_model.hide_exposure_roads()


def remove_datasource(*args):

    # Get index of selected item and check length
    fn_index = app.gui.getvar("modelmaker_fiat", "selected_model_boundary")
    list_model_boundaries = app.gui.getvar(
        "modelmaker_fiat", "model_boundary_file_list"
    )
    if fn_index > len(list_model_boundaries) or fn_index == len(list_model_boundaries):
        fn_index = 0

    # Update item list (file name)
    list_model_boundaries.remove(list_model_boundaries[fn_index])
    app.gui.setvar("modelmaker_fiat", "model_boundary_file_list", list_model_boundaries)

    # Update item value (file path)
    fn_list_model_boundaries = app.gui.getvar(
        "modelmaker_fiat", "fn_model_boundary_file_list"
    )
    fn_list_model_boundaries.remove(fn_list_model_boundaries[fn_index])
    app.gui.setvar(
        "modelmaker_fiat", "fn_model_boundary_file_list", fn_list_model_boundaries
    )
