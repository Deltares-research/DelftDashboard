# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import rasterio
import toml
from pyproj import CRS

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app

from cht_utils import geotiff_to_cog, netcdf_to_cog, xyz_to_cog

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()

        self.name = name
        self.long_name = "Bathymetry"

    def initialize(self):
        
        # Set GUI variables
        group = "bathymetry"
        app.gui.setvar(group, "import_file_format_names", ["GeoTIFF", "NetCDF", "XYZ"])
        app.gui.setvar(group, "import_file_format_values", ["geotiff", "netcdf", "xyz"])
        app.gui.setvar(group, "import_file_format", "geotiff")
        app.gui.setvar(group, "import_file_filter", "GeoTIFF (*.tif;*.tiff)")
        app.gui.setvar(group, "import_file_selected", False)        
        app.gui.setvar(group, "import_file_name", "")
        app.gui.setvar(group, "import_as", "cog")

        app.gui.setvar(group, "dataset_name", "")
        app.gui.setvar(group, "dataset_long_name", "")
        app.gui.setvar(group, "dataset_source", "")

        app.gui.setvar(group, "variable_names", [])
        app.gui.setvar(group, "variable_name", "")

    def set_layer_mode(self, mode):
        pass

    def add_layers(self):
        pass

    def import_dataset(self):

        fmt = app.gui.getvar("bathymetry", "import_file_format")
        import_as = app.gui.getvar("bathymetry", "import_as")
        filename = app.gui.getvar("bathymetry", "import_file_name")
        name = app.gui.getvar("bathymetry", "dataset_name")
        long_name = app.gui.getvar("bathymetry", "dataset_long_name")
        src = app.gui.getvar("bathymetry", "dataset_source")

        # Check if name is al 
        short_names, long_names, source_names = app.bathymetry_database.dataset_names()
        if name in short_names:
            yes = app.gui.window.dialog_yes_no("Dataset name already exists! Do you want to overwrite it?", "")
            if not yes:
                return      

        if import_as == "cog":

            dbpath = app.bathymetry_database.path
            output_dir = os.path.join(dbpath, name)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename_cog = os.path.join(output_dir, name + ".tif")    

            # COG
            if fmt == "geotiff":
                is_cog = False
                # Check if file is cloud optimized
                with rasterio.open(filename) as fff:
                    if fff.is_cog:
                        is_cog = True
                if not is_cog:
                    # Convert to cloud optimized GeoTIFF
                    geotiff_to_cog.geotiff_to_cog(filename, filename_cog)
                    
            elif fmt == "netcdf":
                variable_name = app.gui.getvar("bathymetry", "variable_name")
                wb = app.gui.window.dialog_wait("Generating Cloud Optimized GeoTIFF ...")
                ok = netcdf_to_cog.netcdf_to_cog(filename, variable_name, filename_cog)
                wb.close()

            elif fmt == "xyz":
                crs = app.map.crs
                xyz_to_cog.xyz_to_cog(filename, filename_cog, crs)

            # Check if output file was created
            if not os.path.exists(filename_cog):
                # Add to database
                app.gui.window.dialog_warning("An error occurred while importing dataset!", "Error")    
                return
            
            # Now write the toml metadata file
            # Use rasterio to get the metadata
            with rasterio.open(filename_cog) as fff:
                metadata = fff.meta.copy()
                # Get the CRS
                crs = fff.crs

            crs = CRS(crs)

            meta = {}
            meta["long_name"] = app.gui.getvar("bathymetry", "dataset_long_name")
            meta["format"] = "cog"
            meta["source"] = src
            meta["filename"] = os.path.basename(filename_cog)
            meta["coord_ref_sys_name"] = crs.name
            meta["coord_ref_sys_kind"] = "projected" if crs.is_projected else "geographic"
            meta["vertical_reference_level"] = "unknown"
            meta["vertical_units"] = "m"
            meta["difference_with_msl"] = 0.0

            # Skip description for now
            # write meta to toml file using toml.dump
            meta_file = os.path.join(output_dir, "metadata.tml")
            with open(meta_file, "w") as f:
                f.write(toml.dumps(meta))


        else:
            # Tiles
            # Give warning that this option is not implemented yet
            app.gui.window.dialog_warning("Warning", "Tiles option is not implemented yet. Please use COG option.")

        # Now read in the bathymetry database file and add the dataset to it

        tml_file = os.path.join(dbpath, "bathymetry.tml")
        datasets = toml.load(tml_file)

        # Check if dataset already exists
        for dataset in datasets["dataset"]:
            if dataset["name"] == name:
                return
        datasets["dataset"].append({"name": name})
        # And write it back to the file
        with open(tml_file, "w") as f:
            f.write(toml.dumps(datasets))

        # And finally add the new dataset to the menu
         # topo_menu = app.gui.window.find_menu_item_by_id("topography")
        source_menu = app.gui.window.find_menu_item_by_id("topography." + src)
        if source_menu is None:
            # Need to add source menu to the topography menu
            source_menu = {}
            source_menu["text"] = src
            source_menu["id"] = "topography." + src
            source_menu["menu"] = []
            app.gui.window.add_menu_from_dict(source_menu, "topography", has_children=True)
        # Now add the dataset to the source menu    
        dependency = [{"action": "check",
                        "checkfor": "all",
                        "check": [{"variable": "topography_dataset",
                                    "operator": "eq",
                                    "value": name}]
                        }]
                
        dataset_menu = {"id": "topography." + name,
                        "variable_group": "view_settings",
                        "text": long_name,
                        "separator": False,
                        "checkable": True,
                        "option": name,
                        "method": "select_dataset",
                        "dependency": dependency}
        app.gui.window.add_menu_from_dict(dataset_menu, "topography." + src, has_children=False)

        app.bathymetry_database.load_dataset(name)

        app.gui.window.dialog_info("Dataset imported successfully! It has been added to the Topography menu.", "Success")

    def export_dataset(self):
        # First check if dataset name is valid
        if not self.check_dataset_name():
            return


    def check_dataset_name(self):
        # Check if dataset name is valid
        name = app.gui.getvar("bathymetry", "dataset_name")
        # Check for any special characters except for _ and -
        if not name.isalnum() and "_" not in name and "-" not in name:
            app.gui.window.dialog("Error", "Dataset name can only contain letters, numbers, _ and -")
            return False
        return True


    # def import_geotiff(self, filename):

    #     # Import a GeoTIFF file
    #     # This is a placeholder implementation. The actual implementation will depend on the specific requirements of the application.
    #     print(f"Importing GeoTIFF file: {filename}")

    #     # Check if file is already cloud optimized
    #     filename = app.gui.getvar("bathymetry", "import_file_name")

    #     is_cog = False
    #     # Check if file is cloud optimized
    #     with rasterio.open(filename) as src:
    #         if src.is_cog:
    #             is_cog = True
    #             # Give warning that file is already cloud optimized
    #             app.gui.window.dialog("Warning", "File is already cloud optimized. No need to import again.")

    #     if not is_cog:
    #         # Convert to cloud optimized GeoTIFF
    #         pass

    # def import_netcdf(self, filename):
    #     # Import a NetCDF file
    #     # This is a placeholder implementation. The actual implementation will depend on the specific requirements of the application.
    #     print(f"Importing NetCDF file: {filename}")
    #     # Add your code to import the NetCDF file here 

    # def import_xyz(self, filename):
    #     # Import an XYZ file
    #     # This is a placeholder implementation. The actual implementation will depend on the specific requirements of the application.
    #     print(f"Importing XYZ file: {filename}")
    #     # Add your code to import the XYZ file here
    
