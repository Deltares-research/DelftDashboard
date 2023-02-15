import numpy as np
import geopandas as gpd
import shapely

from ddb import ddb
from guitares.gui import find_element_by_id


def open():
    pass

def map_ready():
    mp = find_element_by_id(ddb.gui.popup_config["element"], "utm_map")["widget"]
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
    layer.add_geojson_layer("polygons",
                            data=gdf,
                            file_name="utm_zones.geojson",
                            select=select_utm_zone,
                            type="polygon_selector",
                            selection_type="single")

def map_moved(coords):
    pass

def select_utm_zone(feature):
    ddb.gui.popup_data = feature["properties"]
