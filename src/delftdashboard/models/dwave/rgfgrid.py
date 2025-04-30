# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 10:23:38 2025

@author: jveeramony
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator, griddata

class RGFGrid:
    def __init__(self, X=None, Y=None, file_name=None):
        """
        Initialize the RGFGrid object with optional X and Y coordinates.
        If file or valid X and Y are not provided, an empty grid is created.
        If a file is provided, the grid will be read from it. And if there is
        a .dep file in the same location, the depths will be initialized with
        those values. Otherwise, it will be initialized to an empty array

        Args:
            X (ndarray, optional): 1D or 2D array for the X coordinates.
            Y (ndarray, optional): 1D or 2D array for the Y coordinates.
            file_name(string, optional): Name of .grd file

        Example usage
        1. Initialize with no arguments
        grid = RGFGrid()

        2. Initialize with valid 1D/2D inputs
        grid = RGFGrid(X=X, Y=Y)

        3. Read from file
        grid = RGFGrid(file_name=grd_file)

        """
        # Initialize other grid properties
        self.X = np.empty((0, 0))
        self.Y = np.empty((0, 0))
        self.Z = np.empty((0, 0))
        self.filename = None
        self.enclosure = None
        self.coordinate_system = 'Spherical'
        self.missing_value = np.nan
        self.grid_type = 'RGF'
        self.orientation = 'anticlockwise'

        if file_name:
            self.filename = Path(file_name) # Convert to Path object
            self.read_grid_from_file(file_name)
            dep_file = self.filename.with_suffix('.dep') # Change extension using pathlib
            self.Z = np.zeros_like(self.X)
            if dep_file.exists(): # Check file existence with pathlib
                self.read_dep_from_file(dep_file)
        elif X is None or Y is None:
            # Initialize with empty arrays if no arguments are provided
            pass
        elif X.ndim == 1 and Y.ndim == 1:
            # Create the right-handed grid using np.meshgrid with 'ij' indexing
            self.X, self.Y = np.meshgrid(X, Y, indexing='ij')
            self.Z = np.zeros_like(self.X)
        elif X.ndim == 2 and Y.ndim == 2 and X.shape == Y.shape:
            # Directly assign the 2D arrays
            self.X = X
            self.Y = Y
            self.Z = np.zeros_like(self.X)
        else:
            # Handle invalid inputs
            print(f"Warning: Invalid inputs. X and Y should be either 1D arrays or 2D arrays of the same shape. "
                  f"Received shapes: X={None if X is None else X.shape}, Y={None if Y is None else Y.shape}. "
                  f"Initialized to empty arrays.")

    def plot(self, ax: plt.Axes = None, edge_color: str = "black"):
        """
        Plot the grid points using Matplotlib.
        """
        # Create figure and axis if none is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 6))
        else:
            fig = ax.figure  # Get the figure associated with the axis

        # Plot edges (grid structure)
        for i in range(self.X.shape[0]):  # Loop over rows (horizontal lines)
            ax.plot(self.X[i, :], self.Y[i, :], color=edge_color, linewidth=0.8, alpha=0.5)
        for j in range(self.X.shape[1]):  # Loop over columns (vertical lines)
            ax.plot(self.X[:, j], self.Y[:, j], color=edge_color, linewidth=0.8, alpha=0.5)

        return ax

    def interpolate_to_grid(self, x, y, z, method='linear'):
        """
        Interpolates the given (x, y, z) data onto the grid (self.X, self.Y).

        Parameters:
        x (np.array): 1D array of x coordinates of the data points.
        y (np.array): 1D array of y coordinates of the data points.
        z (np.array): 1D/2D array of z values of the data points.
        method (str): Interpolation method ('linear', 'nearest', 'cubic'). Default is 'linear'.

        Returns:
        np.array: Interpolated Z values on the grid (self.X, self.Y).
        """
        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)

        if x.ndim == 1 and y.ndim ==1 and z.ndim == 2:
            if z.shape != (len(y), len(x)):
                print("Something wrong with the arrays used for bathymetry")
                print(f'dimensions are {x.shape}, {y.shape}, {z.shape}')
                return
            else:
                points = np.column_stack((self.X.ravel(), self.Y.ravel()))
                interpolator = RegularGridInterpolator((x, y),
                                                       z.T,
                                                       bounds_error=False,
                                                       fill_value=-999
                                                       )
                self.Z = interpolator(points).reshape(self.X.shape)
        elif x.shape == y.shape == z.shape:
            if x.ndim == 1:
                # Stack x and y coordinates into a 2D array of points
                points = np.column_stack((x, y))

                # Perform griddata interpolation on the structured grid
                self.Z = griddata(points, z, (self.X, self.Y), method=method)
        else:
            print("Something wrong with the arrays used for bathymetry")
            print(f'dimensions are {x.shape}, {y.shape}, {z.shape}')

        return self

    def write_grid_to_file(self, filename=None):
        """
        Writes the grid data to a file in a format similar to the MATLAB code.

        Parameters:
        filename (str): The name of the file to write the grid data to. If None, it uses self.filename.
        """
        if filename is None:
            filename = self.filename
        if not filename:
            raise ValueError("No filename specified.")

        # Ensure the filename has a .grd extension
        if filename.suffix != '.grd':
            filename += '.grd'

        try:
            with open(filename, 'w') as file:
                # Write the coordinate system
                file.write(f'Coordinate System = {self.coordinate_system}\n')

                # Write the missing value
                if np.isnan(self.missing_value):
                    missing_value = 0
                else:
                    missing_value = self.missing_value
                file.write(f'Missing Value = {missing_value:25.17e}\n')


                # Write the dimensions of the grid
                file.write(f'{self.X.shape[0]:8}{self.X.shape[1]:8}\n')

                # Write a placeholder for offsets (just as in the MATLAB code)
                file.write(f'{0:8}{0:8}{0:8}\n')

                # Define chunk size for rows
                chunk_size = 5

                # Write the grid data (X and Y) row by row
                M = self.X.shape[0]
                for fld in ['X', 'Y']:
                    coords = getattr(self, fld)
                    coords = np.nan_to_num(coords, nan=missing_value) # Change nan's to missing value

                    for j in range(coords.shape[1]):
                        # Start the line with the ETA label
                        line = f' ETA={j + 1:5}'

                        # Iterate through rows in chunks of `chunk_size`
                        for i in range(0, M, chunk_size):
                            # Add data to the line for the first chunk or create a new indented line
                            chunk = [f'{coords[k, j]:20.12E}' for k in range(i, min(i + chunk_size, M))]
                            if i == 0:
                                # Append to the first line after ETA
                                line += ' ' + ' '.join(chunk) + '\n'
                            else:
                                # Create a new indented line for subsequent chunks
                                line += ' ' * 11 + ' '.join(chunk) + '\n'

                        # Write the formatted line to the file
                        file.write(line)
                    # for j in range(coords.shape[1]):
                    #     file.write(f' ETA={j + 1:5}\n')
                    #     # Write data in chunks of 5 rows
                    #     for i in range(0, M, 5):
                    #         file.write(' '.join([f'{coords[k, j]:22.14e}' for k in range(i, min(i + 5, M))]) + '\n')
            print(f"Grid file {filename} written successfully.")

        except Exception as e:
            raise IOError(f"Error writing to file {filename}: {e}")

    def read_grid_from_file(self, filename=None):
        """
        Reads grid data from a file in the format written by `write_grid_to_file`.

        Parameters:
        filename (str): The name of the file to read the grid data from. If None, it uses self.filename.

        Returns:
        None

        EXAMPLE USAGE:
        # Initialize the grid with placeholders
        grid = RGFGrid(np.zeros((2, 2)), np.zeros((2, 2)))
        grid.filename = 'output_grid.grd'
        # Read the grid from file
        grid.read_grid_from_file()
        print("X Grid:\n", grid.X)
        print("Y Grid:\n", grid.Y)

        """
        if filename is None:
            filename = self.filename
        if not filename:
            raise ValueError("No filename specified.")

        # Ensure the filename has a .grd extension
        if not filename.endswith('.grd'):
            raise ValueError("File must have a .grd extension.")

        with open(filename, 'r') as f:
            lines = f.readlines()

        # Extract the coordinate system if specified
        for line in lines:
            if line.strip().startswith("Coordinate"):
                self.coordinate_system = line.split("=")[-1].strip()
                break
        # Extract the missing value if specified, otherwise set it to zero (Is this correct?)
        self.missing_value = 0.0
        for line in lines:
            if line.strip().startswith("Missing"):
                self.missing_value = float(line.split("=")[-1].strip())
                break
        # Skip all lines before the first 'ETA='
        data_start_index = next(i for i, line in enumerate(lines) if line.strip().startswith("ETA="))

        # Extract grid dimensions (ncols, nrows)
        grid_size_line = next(line for line in lines[:data_start_index] if line.strip() and line.strip()[0].isdigit())
        ncols, nrows = map(int, grid_size_line.split())

        # Initialize empty arrays for X and Y grid data
        X = np.zeros((nrows, ncols))
        Y = np.zeros((nrows, ncols))

        buffer = []
        row_counter = 0
        is_reading_x = True  # Start with X values

        for line in lines[data_start_index:]:
            # If the line starts with ETA=, process the current buffer and switch rows
            if line.strip().startswith("ETA="):
                if buffer:
                    # Assign buffer values to X or Y, depending on the current mode
                    if is_reading_x:
                        X[row_counter, :] = buffer[:ncols]
                    else:
                        Y[row_counter, :] = buffer[:ncols]
                    buffer = buffer[ncols:]  # Clear the buffer for the next row
                    row_counter += 1

                # If we've reached the end of rows for X, switch to reading Y
                if row_counter == nrows:
                    row_counter = 0
                    is_reading_x = not is_reading_x

                # Add new data from the current ETA line to the buffer
                buffer.extend(map(float, line.split()[2:]))
            else:
                # Append grid data values to the buffer
                buffer.extend(map(float, line.split()))

        # Process the last row for X or Y if buffer still has data
        if buffer:
            if is_reading_x:
                X[row_counter, :] = buffer[:ncols]
            else:
                Y[row_counter, :] = buffer[:ncols]

        # If missing values are not set, set it to zero
        if not self.missing_value:
            self.missing_value = 0.0

        self.X = X.T
        self.Y = Y.T

        # # Set all missing values to nan's
        # self.X[self.X == missing_value] = np.nan
        # self.Y[self.Y == missing_value] = np.nan

    def write_dep_to_file(self, filename=None, missing_value=-999):
        """
        Writes the Z values to a file in a specific format.

        Parameters:
        filename (str): The name of the file to write to. Defaults to self.filename.
        missing_value (float): The value to use for missing data (NaN). Default is -999.
        """
        if filename is None:
            # Use grid's filename if none provided
            filename = self.filename.with_suffix(".dep")

        if not filename:
            raise ValueError("Filename must be provided.")

        # Ensure the filename has a .dep extension
        if filename.suffix != '.dep':
            filename = filename.with_suffix('.dep')

        if self.Z is None or (isinstance(self.Z, np.ndarray) and self.Z.size == 0):
            raise ValueError("No Z values available to write.")

        # Open file for writing in ASCII mode
        with open(filename, 'w', encoding='ascii') as fid:
            DP = self.Z.copy()

            # Create the extended matrix for Z values with an extra row/column of missing values (-999)
            DPX = np.vstack([np.hstack([DP, missing_value * np.ones((DP.shape[0], 1))]),
                             missing_value * np.ones((1, DP.shape[1] + 1))])

            # Replace NaN values with the missing value (-999)
            DPX[np.isnan(DPX)] = missing_value

            # Transpose the file
            DPX = DPX.T

            # Define the format for output, similar to the MATLAB format
            rows, cols = DPX.shape

            # Prepare a format string for 12 values per line
            format_str = '  {:14.7E}'  # Define the format for each value
            # line_format = (format_str * 12 + '\n')  # Line format for 12 values per line

            # Write the array to the file in row-major order
            for row in DPX:
                # Split the row into chunks of 12 values and write each chunk
                for i in range(0, len(row), 12):
                    chunk = row[i:i+12]
                    fid.write(''.join(format_str.format(val) for val in chunk) + '\n')

        print(f"File {filename} written successfully.")

    def read_dep_from_file(self, filename=None, missing_value=-999):
        """
        Reads Z values from a .dep file into the grid.

        Parameters:
        filename (str): The name of the file to read from. Defaults to self.filename.
        missing_value (float): The value used for missing data. Default is -999.

        Returns:
        numpy.ndarray: A 2D array of Z values read from the file.
        """
        if filename is None:
            filename = self.filename  # Use grid's filename if none provided

        if not filename:
            raise ValueError("Filename must be provided.")

        # Ensure the filename has a .dep extension
        if not filename.endswith('.dep'):
            raise ValueError("File must have a .dep extension.")

        rows, cols = self.Z.shape
        rows += 1
        cols += 1

        data = [] # Flattened data to store all file values
        # Read the file
        with open(filename, 'r', encoding='ascii') as fid:
            for line in fid:
                # Parse line into floating-point values
                values = list(map(float, line.split()))
                data.extend(values)

        # Ensure the data matches the size of the grid
        if len(data) != rows * cols:
            raise ValueError(f"File data size ({len(data)}) does not match grid size ({rows * cols})")

        # Fill the grid
        Z_array = np.array(data).reshape(cols, rows).T
        self.Z = Z_array[:-1, :-1]
