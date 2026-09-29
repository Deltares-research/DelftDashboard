"""Utility functions for generating topobathy COG files."""

import logging

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

logger = logging.getLogger(__name__)


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
        Selected bathymetry datasets, highest priority first.
    bounds : tuple
        (x0, y0, x1, y1) bounding box in the model CRS.
    crs : CRS
        Coordinate reference system.
    topography_data_catalog : TopographyDataCatalog, optional
        HydroMT-based topography catalog.
    bathymetry_database : object, optional
        Legacy cht_bathymetry database.
    dx : float
        Output pixel size (in units of ``crs``).
    """
    x0, y0, x1, y1 = bounds

    # Round outward to a multiple of dx
    x0 = x0 - (x0 % dx)
    x1 = x1 + (dx - x1 % dx)
    y0 = y0 - (y0 % dx)
    y1 = y1 + (dx - y1 % dx)

    # Target grid: this defines the shape and transform of the output raster
    nx = int(np.round((x1 - x0) / dx))
    ny = int(np.round((y1 - y0) / dx))
    transform = from_origin(x0, y1, dx, dx)

    if topography_data_catalog is not None:
        # HydroMT path: fetch each dataset, resample it onto the target grid,
        # and merge with first-selected-dataset-wins priority.
        geom = gpd.GeoDataFrame(geometry=[box(x0, y0, x1, y1)], crs=crs)
        zz = np.full((ny, nx), np.nan, dtype=np.float32)
        for ds in bathymetry_sets:
            name = ds.get("elevation", ds.get("name"))
            zmin = ds.get("zmin", -1.0e9)
            zmax = ds.get("zmax", 1.0e9)
            try:
                # zoom only selects the closest overview level of the source;
                # the actual resampling to dx happens in reproject() below.
                da = topography_data_catalog.get_rasterdataset(
                    name, geom=geom, zoom=(dx, "metre"), buffer=2
                )
                if da.ndim > 2:
                    da = da.squeeze(drop=True)
                da = da.astype(np.float32)
                da.raster.set_nodata(np.nan)
                da = da.raster.reproject(
                    dst_crs=crs,
                    dst_transform=transform,
                    dst_width=nx,
                    dst_height=ny,
                    dst_nodata=np.nan,
                    method="bilinear",
                )
                vals = np.asarray(da.values, dtype=np.float32)
                if vals.shape != (ny, nx):
                    raise ValueError(
                        f"unexpected shape {vals.shape}, expected {(ny, nx)}"
                    )
                vals[(vals < zmin) | (vals > zmax)] = np.nan
                # Fill gaps left by higher-priority datasets
                mask = np.isnan(zz)
                zz[mask] = vals[mask]
            except Exception as e:
                logger.warning(
                    "Skipping dataset '%s' in topobathy geotiff: %s", name, e
                )
                continue
            if not np.isnan(zz).any():
                # Grid is fully covered; lower-priority datasets not needed
                break

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
