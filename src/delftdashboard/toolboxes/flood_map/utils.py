import numpy as np
import rasterio
from rasterio.transform import from_origin

def make_topobathy_cog(filename,
                       bathymetry_sets,
                       bounds,
                       crs,
                       bathymetry_database=None,
                       dx=10.0):
    
    """Make a COG file with topobathy. Now only works for projected coordinates. This always make the topobathy COG in the same projection as the model."""

    x0 = bounds[0]
    y0 = bounds[1]
    x1 = bounds[2]
    y1 = bounds[3]

    # Round up and down to nearest dx
    x0 = x0 - (x0 % dx)
    x1 = x1 + (dx - x1 % dx)
    y0 = y0 - (y0 % dx)
    y1 = y1 + (dx - y1 % dx)

    xx = np.arange(x0, x1, dx) + 0.5 * dx
    yy = np.arange(y1, y0, -dx) - 0.5 * dx
    zz = np.empty((len(yy), len(xx),), dtype=np.float32)

    xx, yy = np.meshgrid(xx, yy)
    zz = bathymetry_database.get_bathymetry_on_points(xx,
                                                        yy,
                                                        dx,
                                                        crs,
                                                        bathymetry_sets)

    # And now to cog (use -999 as the nodata value)
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

def make_topobathy_cog_chunked(
    filename,
    bathymetry_sets,
    bounds,
    crs,
    bathymetry_database=None,
    dx=10.0,
    blocksize=1024,
):
    """
    Make a COG file with topobathy in chunks.
    Works for large rasters without blowing up memory.
    """

    x0 = bounds[0]
    y0 = bounds[1]
    x1 = bounds[2]
    y1 = bounds[3]

    # Round up and down to nearest dx
    x0 = x0 - (x0 % dx)
    x1 = x1 + (dx - x1 % dx)
    y0 = y0 - (y0 % dx)
    y1 = y1 + (dx - y1 % dx)

    width = int(np.round((x1 - x0) / dx))
    height = int(np.round((y1 - y0) / dx))

    transform = from_origin(x0, y1, dx, dx)
    nodata = -999.0

    profile = {
        "driver": "COG",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "overview_resampling": Resampling.nearest,
        "blockxsize": blocksize,
        "blockysize": blocksize,
        "tiled": True,
    }

    with rasterio.open(filename, "w", **profile) as dst:

        # Loop through chunks
        for row_off in range(0, height, blocksize):
            for col_off in range(0, width, blocksize):

                win_width = min(blocksize, width - col_off)
                win_height = min(blocksize, height - row_off)
                window = Window(col_off, row_off, win_width, win_height)

                # Compute row/col indices
                rows = np.arange(row_off, row_off + win_height)
                cols = np.arange(col_off, col_off + win_width)

                # Convert to x,y coordinates of pixel centers
                x_coords = transform.c + (cols + 0.5) * transform.a
                y_coords = transform.f + (rows + 0.5) * transform.e
                xx, yy = np.meshgrid(x_coords, y_coords)

                # Query bathymetry
                zz = bathymetry_database.get_bathymetry_on_points(
                    xx, yy, dx, crs, bathymetry_sets
                ).astype("float32")

                # Replace invalid with nodata
                zz = np.where(np.isfinite(zz), zz, nodata)

                # Write chunk into file
                dst.write(zz, 1, window=window)
