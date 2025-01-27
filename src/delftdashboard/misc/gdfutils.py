import geopandas as gpd
import pandas as pd

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
