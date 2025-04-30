# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 13:21:50 2025

@author: jveeramony
"""

import numpy as np
import xarray as xr
import argparse, toml
from pathlib import Path

import rgfgrid, rgfgrid_utils

def update_value(current, value):
    return value if current is None else min(current, value)

if __name__ == "__main__":

    """
    To run this in spyder (use full paths to be safe) -
    Spyder version 5:
        runfile('<this_file>', args='-i <toml_file>')
    Spyder version 6:
        %runfile <this_file>  --args '-i <toml_file>'
    Command line:
        python <this file> -i <toml_file>
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file',
                        help = 'TOML file containing input settings',
                        metavar = 'FILE')
    args = parser.parse_args()

    if args.input_file is None:
        input_path = input('Please provide the path to the TOML file: ').strip()
        toml_file = Path(input_path)
    else:
        toml_file = Path(args.input_file)

    # Read in the toml file; convert to a structure
    try:
        if not toml_file.exists():
            raise FileNotFoundError(f"Error: The file '{toml_file}' does not exist.")

        with toml_file.open("r") as file:
            data = toml.load(file)

        print("TOML file loaded successfully.")

    except FileNotFoundError as e:
        print(e)
    except toml.TomlDecodeError:
        print(f"Error: Failed to parse TOML file '{toml_file}'. Ensure it has valid TOML syntax.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    parameters = rgfgrid_utils.DotDict(data)

    # First check if the bathymetry file exists
    bathy_file = Path(parameters.bathy_file)
    if not bathy_file.is_file():
        print('Bathymetry file does not exist')

    # make dirs
    # Ensure output_dir is a Path object
    output_dir = Path(parameters.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(parameters, "wave"):
        wave_dir = output_dir / "wave"
        wave_dir.mkdir(parents=True, exist_ok=True)

    lat_min, lon_min, lat_max, lon_max = None, None, None, None
    if hasattr(parameters, 'wave'):
        # Iterate over the number of wave domain needed
        for domain in parameters.wave:
            # For readability
            lat_min = update_value(lat_min, domain.lat[0])
            lat_max = update_value(lat_max, domain.lat[1])
            lon_min = update_value(lon_min, domain.lon[0])
            lon_max = update_value(lon_max, domain.lon[1])

    try:
        data_set = xr.open_dataset(parameters.bathy_file)

        # Find the appropriate bathymetry variable
        data_bathy = rgfgrid_utils.find_bathymetry_variable(data_set)

        # If necessary, convert longitudes in data_bathy from [0, 360] to [-180, 180]
        if data_bathy.lon.max() > 180:
            data_bathy = data_bathy.assign_coords(lon=((data_bathy.lon + 180) % 360 - 180))
            data_bathy = data_bathy.sortby("lon")  # Ensure correct ordering after remapping

        # subset bathy to area of interest
        data_bathy_sel = data_bathy.sel(lon=slice(lon_min-1, lon_max+1),
                                        lat=slice(lat_min-1, lat_max+1))
    except:
        print("Bathymetry file does not contain elevation\n")

    # Now generate the wave grids if necessary
    if hasattr(parameters, 'wave'):
        print('Generating wave grids and corresponding bathymetries')
        # Iterate over the number of wave domain needed
        for domain in parameters.wave:

            # Create rectilinear grid
            x = np.arange(domain.lon[0], domain.lon[1], domain.dxy)
            y = np.arange(domain.lat[0], domain.lat[1], domain.dxy)
            grid = rgfgrid.RGFGrid(x, y)

            # Remap the max values since the grid extent can be different due
            # to a odd value for domain.dxy
            domain.lon[1] = np.max(x)
            domain.lat[1] = np.max(y)

            # Get the bathymetry values (SWAN uses positive values for depth)
            X, Y = data_bathy_sel.lon.values, data_bathy_sel.lat.values
            Z = -data_bathy_sel.values

            # Interpolate to grid
            grid.interpolate_to_grid(X, Y, Z)
            grid.filename = wave_dir / f"{domain.name}.grd"
            grid.missing_value = -999

            # Generate boundary points and write to text file
            if hasattr(domain ,'boundary_sides'):
                append = False # This ensures file creation for the first boundary segment
                filename = wave_dir / "boundary.txt"
                for side in domain.boundary_sides:
                    name = "Boundary"+side
                    spectrum_spec = "parametric"
                    shape_type="Jonswap"
                    period_type="peak"
                    dir_spread_type="Power"
                    peak_enhance_fac=3.3
                    if side == 'north':
                        start_x = domain.lon[1]
                        end_x = domain.lon[0]
                        start_y = domain.lat[1]
                        end_y = domain.lat[1]
                        dl = np.abs(start_x - end_x)
                    elif side == 'west':
                        start_x = domain.lon[0]
                        end_x = domain.lon[0]
                        start_y = domain.lat[1]
                        end_y = domain.lat[0]
                        dl = np.abs(start_y - end_y)
                    elif side == 'south':
                        start_x = domain.lon[0]
                        end_x = domain.lon[1]
                        start_y = domain.lat[0]
                        end_y = domain.lat[0]
                        dl = np.abs(start_x - end_x)
                    elif side == 'east':
                        start_x = domain.lon[1]
                        end_x = domain.lon[1]
                        start_y = domain.lat[0]
                        end_y = domain.lat[1]
                        dl = np.abs(start_y - end_y)
                    else:
                        print("Unknown boundary side type: Should be north, south, east or west")
                    cond_spec_distances = np.arange(0, dl, domain.ds)
                    cond_spec_distances = np.append(cond_spec_distances, dl)
                    rgfgrid_utils.write_wave_boundary(name, start_x, end_x,
                                                   start_y, end_y,
                                                   spectrum_spec,
                                                   shape_type,
                                                   period_type,
                                                   dir_spread_type,
                                                   peak_enhance_fac,
                                                   cond_spec_distances,
                                                   filename,
                                                   append
                                                   )
                    append = True # Now append the rest of the boundaries

            # Write the files
            grid.write_grid_to_file()  # Write the grid to the file
            grid.write_dep_to_file() # Write the depth file