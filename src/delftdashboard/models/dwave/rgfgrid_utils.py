# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 13:24:30 2025

@author: jveeramony
"""
import sys

class DotDict:
    """
    recursively converts any nested dictionary into a DotDict object in the
    constructor handling lists containing dictionaries (e.g., wave input).
    To handle this properly, we need to modify the constructor to recursively
    convert dictionaries inside lists into DotDict instances as well.

    """
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                value = DotDict(value)  # Recursively convert nested dictionaries
            elif isinstance(value, list):
                value = [
                    DotDict(item) if isinstance(item, dict) else item
                    for item in value
                ]  # Convert dictionaries inside lists
            setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = DotDict(value)
        elif isinstance(value, list):
            value = [
                DotDict(item) if isinstance(item, dict) else item
                for item in value
            ]
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def to_dict(self):
        """Convert DotDict back to a standard dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DotDict):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [
                    item.to_dict() if isinstance(item, DotDict) else item
                    for item in value
                ]
            result[key] = value
        return result

def find_bathymetry_variable(ds, preferred_var=None):
    """
    Identifies the correct bathymetry variable in an xarray dataset.

    Parameters:
    - ds: xarray.Dataset, the opened dataset.
    - preferred_var: str, optional user-specified preferred variable name.

    Returns:
    - xarray.DataArray of the selected variable.

    Raises:
    - ValueError if no suitable variable is found.
    """
    # If the preferred variable exists, use it
    if preferred_var and preferred_var in ds:
        return ds[preferred_var]

    # Common bathymetry variable names
    possible_vars = ["z", "elevation", "depth", "topo", "bathymetry"]

    # Find the first matching variable in the dataset
    for var in possible_vars:
        if var in ds:
            return ds[var]

    # Fallback: Try detecting variables with relevant attributes
    for var in ds.data_vars:
        attrs = ds[var].attrs
        if any(keyword in str(attrs.get("long_name", "")).lower() for keyword in ["topography", "bathymetry", "depth", "elevation"]):
            return ds[var]

    # If no suitable variable is found, raise an error
    raise ValueError(f"No recognized bathymetry variable found. Available variables: {list(ds.data_vars)}")
    sys.exit()

def write_wave_boundary(
    name, start_x, end_x, start_y, end_y,
    spectrum_spec, shape_type, period_type, dir_spread_type,
    peak_enhance_fac, cond_spec_distances, filename=None, append=False
):
    """
    Generate a formatted boundary definition and optionally save it to a file.

    Parameters:
        name (str): Boundary name.
        start_x (float): Start X-coordinate.
        end_x (float): End X-coordinate.
        start_y (float): Start Y-coordinate.
        end_y (float): End Y-coordinate.
        spectrum_spec (str): Spectrum specification type.
        shape_type (str): Shape type (e.g., Jonswap).
        period_type (str): Period type (e.g., peak).
        dir_spread_type (str): Directional spread type.
        peak_enhance_fac (float): Peak enhancement factor.
        cond_spec_distances (list of float): List of distances for conditional specification.
        filename (str, optional): If provided, saves the definition to this file.
        append (bool, optional): If True, appends to the file instead of overwriting. Default is False.

    Returns:
        str: The formatted boundary definition.
    """
    # Create the formatted output
    output = "[Boundary]\n"
    output += f"    Name                  = {name}\n"
    output +=  "    Definition            = xy-coordinates\n"
    output += f"    StartCoordX           = {start_x:-.7f}\n"
    output += f"    EndCoordX             = {end_x:-.7f}\n"
    output += f"    StartCoordY           = {start_y:-.7f}\n"
    output += f"    EndCoordY             = {end_y:-.7f}\n"
    output += f"    SpectrumSpec          = {spectrum_spec}\n"
    output += f"    SpShapeType           = {shape_type}\n"
    output += f"    PeriodType            = {period_type}\n"
    output += f"    DirSpreadType         = {dir_spread_type}\n"
    output += f"    PeakEnhanceFac        = {peak_enhance_fac:-.7e}\n"

    # Add conditional specifications
    for dist in cond_spec_distances:
        output += f"    CondSpecAtDist        = {dist:-.7f}\n"

    # Optionally write or append to a file
    if filename:
        mode = "a" if append else "w"  # 'a' for append, 'w' for overwrite
        with open(filename, mode) as file:
            file.write(output)

    return
