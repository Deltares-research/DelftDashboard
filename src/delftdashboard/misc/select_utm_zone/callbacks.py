import numpy as np
import geopandas as gpd
import shapely

from delftdashboard.app import app

def open():
    pass

def map_ready(*args):
    mp = app.gui.popup_window["utm_zone"].find_element_by_id("utm_map").widget
    mp.jump_to(0.0, 0.0, 1)
    # Add UTM polygons
    lon = np.arange(-180.0, 180.0, 6.0)
    lat = np.arange(-80.0, 80.0, 8.0)
    letters = ['C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X']
    gdf_list = []
    for ilon, x in enumerate(lon):
        point = shapely.geometry.Point(x + 3.0, 0.0)
        gdf_list.append({"utm_number": str(ilon + 1), "geometry": point})
        for ilat, y in enumerate(lat):
            if y < 0.0:
                utm_zone = str(ilon + 1) + "S"
            else:
                utm_zone = str(ilon + 1) + "N"
            utm_letter = letters[ilat]
            polygon = shapely.geometry.Polygon([[x, y], [x + 6.0, y], [x + 6.0, y + 8.0], [x, y + 8]])
            gdf_list.append({"utm_zone": utm_zone, "utm_letter": letters[ilat], "geometry": polygon})
    gdf = gpd.GeoDataFrame(gdf_list, crs=4326)
    layer = mp.add_layer("utm")
    polygon_layer = layer.add_layer("polygons", type="polygon_selector",
                    file_name="utm_zones.geojson",
                    select=select_utm_zone,
                    selection_type="single",
                    fill_opacity=0.0,
                    fill_opacity_selected=1.0,
                    hover_property="utm_zone")
    polygon_layer.set_data(gdf, 0)

def map_moved(*args):
    pass

def select_utm_zone(feature, widget):
    app.gui.popup_data["utm_zone"] = feature["properties"]
