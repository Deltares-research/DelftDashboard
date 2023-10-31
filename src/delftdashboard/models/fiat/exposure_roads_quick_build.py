from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args):
    # De-activate existing layers
    map.update()


def set_variables(*args):
    app.model["fiat"].set_input_variables()


def build_roads_exposure_osm(*args):
    try:
        # Get the roads to show in the map
        gdf = app.model["fiat"].domain.exposure_vm.get_osm_roads()

        crs = app.gui.getvar("fiat", "selected_crs")
        gdf.set_crs(crs, inplace=True)

        app.map.layer["fiat"].layer["exposure_lines"].crs = crs
        app.map.layer["fiat"].layer["exposure_lines"].set_data(
            gdf
        )

        app.gui.setvar("fiat", "show_asset_locations", True)

        # Set the road damage threshold
        road_damage_threshold = app.gui.getvar("fiat", "road_damage_threshold")
        app.model["fiat"].domain.vulnerability_vm.set_road_damage_threshold(road_damage_threshold)
    except KeyError:
        app.gui.window.dialog_info(text="No OSM roads found in this area, try another or a larger area.", title="No OSM roads found")
    