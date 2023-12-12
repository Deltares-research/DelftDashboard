import geopandas as gpd
import pandas as pd
import time
from pathlib import Path

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
            shape="rectangle",
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


def draw_boundary(*args):
    selected_method = app.gui.getvar("modelmaker_fiat", "selected_aoi_method")
    if selected_method == "polygon":
        draw_polygon()
    elif selected_method == "box":
        draw_bbox()
    elif selected_method == "sfincs":
        print("Not yet implemented")
        pass
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
        app.active_model.new()

    gdf = app.map.layer["modelmaker_fiat"].layer[active_layer].get_gdf()
    app.active_toolbox.area_of_interest = gdf
    gdf.to_file(
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


def load_aoi_file():
    clear_aoi_layers()

    fname = app.gui.window.dialog_open_file(
        "Select Area of Interest File", filter="*.shp *.geojson *.gpkg"
    )
    if fname[0]:
        gdf = gpd.read_file(fname[0])

        # Add the polygon to the map
        layer = app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_file"]
        layer.set_data(gdf)
        app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
        app.gui.setvar(
            "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_file"
        )

        app.active_toolbox.area_of_interest = gdf

        # Fly to the site
        zoom_to_boundary()


def load_sfincs_domain(*args):
    clear_aoi_layers()

    group = "sfincs_hmt"
    lenx = app.gui.getvar(group, "dx") * app.gui.getvar(group, "mmax")
    leny = app.gui.getvar(group, "dy") * app.gui.getvar(group, "nmax")

    app.map.layer["modelmaker_fiat"].layer["area_of_interest_from_sfincs"].crs = app.crs
    app.map.layer["modelmaker_fiat"].layer[
        "area_of_interest_from_sfincs"
    ].add_rectangle(
        app.gui.getvar(group, "x0"),
        app.gui.getvar(group, "y0"),
        lenx,
        leny,
        app.gui.getvar(group, "rotation"),
    )
    app.gui.setvar("modelmaker_fiat", "area_of_interest", 1)
    app.gui.setvar(
        "modelmaker_fiat", "active_area_of_interest", "area_of_interest_from_sfincs"
    )


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
        app.active_model.new()

    ## BUILDINGS ##
    model = "fiat"
    checkbox_group = "_main"
    try:
        dlg = app.gui.window.dialog_wait("\nDownloading NSI data...")
        app.gui.setvar(model, "created_nsi_assets", "nsi")
        app.gui.setvar(
            model, "text_feedback_create_asset_locations", "NSI assets created"
        )

        crs = app.gui.getvar(model, "selected_crs")
        (
            gdf,
            unique_primary_types,
            unique_secondary_types,
        ) = app.active_model.domain.exposure_vm.set_asset_locations_source(
            source="NSI", ground_floor_height="NSI", crs=crs
        )
        gdf.set_crs(crs, inplace=True)

        # Set the buildings attribute to gdf for easy visualization of the buildings
        app.active_model.buildings = gdf

        list_types = list(gdf["Secondary Object Type"].unique())
        list_types.sort()
        df = pd.DataFrame(
            data={
                "Secondary Object Type": list_types,
                "Assigned: Structure": "",
                "Assigned: Content": "",
            }
        )
        ## TODO: add the nr of stories and the basement

        app.gui.setvar(model, "exposure_categories_to_link", df)

        app.map.layer["buildings"].layer["exposure_points"].crs = crs
        app.map.layer["buildings"].layer["exposure_points"].set_data(gdf)

        app.gui.setvar(
            model, "selected_primary_classification_string", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_string", unique_secondary_types
        )
        app.gui.setvar(
            model, "selected_primary_classification_value", unique_primary_types
        )
        app.gui.setvar(
            model, "selected_secondary_classification_value", unique_secondary_types
        )

        app.gui.setvar(model, "show_asset_locations", True)
        app.gui.setvar("modelmaker_fiat", "show_asset_locations", True)

        # Set the damage curves
        selected_damage_curve_database = "default_vulnerability_curves"
        selected_link_table = "default_hazus_iwr_linking"
        app.gui.setvar(
            model, "selected_damage_curve_database", selected_damage_curve_database
        )
        app.gui.setvar(
            model, "selected_damage_curve_linking_table", selected_link_table
        )
        app.active_model.domain.vulnerability_vm.add_vulnerability_curves_to_model(
            selected_damage_curve_database, selected_link_table
        )

        # Check the checkbox
        app.gui.setvar("_main", "checkbox_vulnerability", True)

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
        app.gui.setvar(checkbox_group, "checkbox_asset_locations", True)
        app.gui.setvar(checkbox_group, "checkbox_classification", True)
        app.gui.setvar(checkbox_group, "checkbox_damage_values", True)
        app.gui.setvar(checkbox_group, "checkbox_finished_floor_height", True)
        app.gui.setvar(checkbox_group, "checkbox_svi_(optional)", True)

        # Set the sources
        app.gui.setvar(model, "source_asset_locations", "National Structure Inventory")
        app.gui.setvar(model, "source_classification", "National Structure Inventory")
        app.gui.setvar(
            model, "source_finished_floor_elevation", "National Structure Inventory"
        )
        app.gui.setvar(
            model, "source_max_potential_damage", "National Structure Inventory"
        )
        app.gui.setvar(model, "source_ground_elevation", "National Structure Inventory")

        dlg.close()

    except FileNotFoundError:
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )
        dlg.close()

    ## ROADS ##
    try:
        dlg = app.gui.window.dialog_wait("\nDownloading OSM data...")

        # Get the roads to show in the map
        # By default it is taking the following road types:
        # "motorway",
        # "motorway_link",
        # "trunk",
        # "trunk_link",
        # "primary",
        # "primary_link",
        # "secondary",
        # "secondary_link",

        gdf = app.active_model.domain.exposure_vm.get_osm_roads()

        crs = app.gui.getvar("fiat", "selected_crs")
        gdf.set_crs(crs, inplace=True)

        app.map.layer["roads"].layer["exposure_lines"].crs = crs
        app.map.layer["roads"].layer["exposure_lines"].set_data(gdf)

        # Set the road damage threshold
        road_damage_threshold = app.gui.getvar("fiat", "road_damage_threshold")
        app.active_model.domain.vulnerability_vm.set_road_damage_threshold(
            road_damage_threshold
        )

        # Show the roads
        app.active_model.show_exposure_roads()
        app.gui.setvar("_main", "checkbox_roads_(optional)", True)

        # Set the checkbox checked
        app.gui.setvar("fiat", "show_roads", True)
        app.gui.setvar("modelmaker_fiat", "show_roads", True)

        dlg.close()
    except Exception:
        app.gui.window.dialog_info(
            text="No OSM roads found in this area, try another or a larger area.",
            title="No OSM roads found",
        )
        dlg.close()


def display_asset_locations(*args):
    """Show/hide buildings layer"""
    app.gui.setvar("fiat", "show_asset_locations", args[0])
    if args[0]:
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
