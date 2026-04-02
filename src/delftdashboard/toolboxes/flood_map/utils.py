"""Utility functions for generating topobathy COG files."""

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box


def make_topobathy_cog(
    filename,
    bathymetry_sets,
    bounds,
    crs,
    topography_data_catalog=None,
    bathymetry_database=None,
    dx=10.0,
):
    """Make a Cloud Optimized GeoTIFF with topobathy data.

    Supports two paths:
    - ``topography_data_catalog``: fetches data via the hydromt data catalog
    - ``bathymetry_database``: legacy path using cht_bathymetry

    Parameters
    ----------
    filename : str
        Output COG file path.
    bathymetry_sets : list of dict
        Selected bathymetry datasets.
    bounds : tuple
        (x0, y0, x1, y1) bounding box in the model CRS.
    crs : CRS
        Coordinate reference system.
    topography_data_catalog : TopographyDataCatalog, optional
        HydroMT-based topography catalog.
    bathymetry_database : object, optional
        Legacy cht_bathymetry database.
    dx : float
        Output pixel size.
    """
    x0, y0, x1, y1 = bounds

    # Round to nearest dx
    x0 = x0 - (x0 % dx)
    x1 = x1 + (dx - x1 % dx)
    y0 = y0 - (y0 % dx)
    y1 = y1 + (dx - y1 % dx)

    if topography_data_catalog is not None:
        # HydroMT path: fetch merged raster from the catalog
        geom = gpd.GeoDataFrame(geometry=[box(x0, y0, x1, y1)], crs=crs)
        zz = None
        for ds in reversed(bathymetry_sets):
            name = ds.get("elevation", ds.get("name"))
            zmin = ds.get("zmin", -1.0e9)
            zmax = ds.get("zmax", 1.0e9)
            try:
                da = topography_data_catalog.get_rasterdataset(
                    name, geom=geom, zoom=(dx, "metre")
                )
                vals = da.values.astype(np.float32)
                vals[(vals < zmin) | (vals > zmax)] = np.nan
                if zz is None:
                    zz = vals
                else:
                    # Fill NaN in zz with this dataset (priority merge)
                    mask = np.isnan(zz)
                    zz[mask] = vals[mask]
            except Exception:
                continue

        if zz is None:
            # No data found at all — create empty array
            nx = int(np.round((x1 - x0) / dx))
            ny = int(np.round((y1 - y0) / dx))
            zz = np.full((ny, nx), np.nan, dtype=np.float32)

    elif bathymetry_database is not None:
        # Legacy cht_bathymetry path
        xx = np.arange(x0, x1, dx) + 0.5 * dx
        yy = np.arange(y1, y0, -dx) - 0.5 * dx
        xx, yy = np.meshgrid(xx, yy)
        zz = bathymetry_database.get_bathymetry_on_points(
            xx, yy, dx, crs, bathymetry_sets
        )
    else:
        raise ValueError(
            "Either topography_data_catalog or bathymetry_database required."
        )

    zz = np.where(np.isfinite(zz), zz, -999.0).astype(np.float32)

    with rasterio.open(
        filename,
        "w",
        driver="COG",
        height=zz.shape[0],
        width=zz.shape[1],
        count=1,
        dtype=zz.dtype,
        crs=crs,
        transform=from_origin(x0, y1, dx, dx),
        nodata=-999.0,
    ) as dst:
        dst.write(zz, 1)
