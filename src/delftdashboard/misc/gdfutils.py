import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def mpol2pol(gdf):
    """
    Convert MultiPolygon to Polygon
    """
    gdfout = gpd.GeoDataFrame()
    # Loop through rows
    for idx, row in gdf.iterrows():
        if row['geometry'].geom_type == 'MultiPolygon':
            # Convert MultiPolygon to Polygon
            # Loop through parts of MultiPolygon
            for i in range(len(row['geometry'].geoms)):
                # Create new row for each part
                gdfnew = gdf.loc[[idx]].copy()
                gdfnew['geometry'] = row['geometry'].geoms[i]
                gdfout = pd.concat([gdfout, gdfnew])
        else:
            gdftmp = gdf.loc[[idx]].copy()
            gdfout = pd.concat([gdfout, gdftmp])
    gdfout.set_crs(gdf.crs)        
    return gdfout

def mline2point(gdf):
    """
    Convert (Multi)LineString to Point
    """

    point_records = []

    for idx, row in gdf.iterrows():
        geom = row.geometry
        base_name  = row['name']  # Preserve the 'name' column

        if geom.geom_type == 'LineString':
            coords = geom.coords
        elif geom.geom_type == 'MultiLineString':
            coords = []
            for part in geom.geoms:
                coords.extend(part.coords)
        else:
            continue  # Skip unsupported geometry types

        for i, coord in enumerate(coords, start=1):
            new_name = f"{base_name}_{str(i).zfill(4)}"
            point_records.append({'geometry': Point(coord), 'name': new_name})

    # Create new GeoDataFrame
    gdf_points = gpd.GeoDataFrame(point_records, crs=gdf.crs)

    return gdf_points