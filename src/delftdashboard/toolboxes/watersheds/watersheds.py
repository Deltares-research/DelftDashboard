# -*- coding: utf-8 -*-
"""
Created on Mon May 10 12:18:09 2021

@author: ormondt
"""
import os
import geopandas as gpd
import fiona
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.ops import transform
import pyproj
# import numpy as np
# from shapely.geometry import box

from delftdashboard.operations.toolbox import GenericToolbox
from delftdashboard.app import app
from delftdashboard.operations import map

# For now, we do need make a separate cht package for the watersheds. Rather, we keep it in Delft Dashboard.
from .cht_watersheds import WatershedsDatabase

class Toolbox(GenericToolbox):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.long_name = "Watersheds"
        self.gdf = gpd.GeoDataFrame()

    def initialize(self):

        # Read the database
        if "watersheds_database_path" not in app.config:
            app.config["watersheds_database_path"] = os.path.join(app.config["data_path"], "watersheds")
        s3_bucket = "deltares-ddb"
        s3_key = f"data/watersheds"
        app.watersheds_database = WatershedsDatabase(path=app.config["watersheds_database_path"],
                                                     s3_bucket=s3_bucket,
                                                     s3_key=s3_key)

        short_names, long_names = app.watersheds_database.dataset_names()
        if len(short_names) == 0:
            short_names = [" "]
            long_names = [" "]

        # GUI variables
        group = "watersheds"
        app.gui.setvar(group, "dataset_names", short_names)
        app.gui.setvar(group, "dataset_long_names", long_names)
        app.gui.setvar(group, "dataset", short_names[0])
        app.gui.setvar(group, "buffer", 100.0)
        app.gui.setvar(group, "level_names", app.watersheds_database.dataset[short_names[0]].level_names)
        app.gui.setvar(group, "level_long_names", app.watersheds_database.dataset[short_names[0]].level_long_names)
        app.gui.setvar(group, "level", app.watersheds_database.dataset[short_names[0]].level_names[0])
        app.gui.setvar(group, "nr_selected_watersheds", 0)

    def select_tab(self):
        map.update()
        app.map.layer["watersheds"].show()
        app.map.layer["watersheds"].layer["boundaries"].activate()
        # self.update_boundaries_on_map()

    def set_layer_mode(self, mode):
        if mode == "inactive":
            # Make all layers invisible
            app.map.layer["watersheds"].hide()
        if mode == "invisible":
            # Make all layers invisible
            app.map.layer["watersheds"].hide()

    def add_layers(self):
        # Add Mapbox layers
        layer = app.map.add_layer("watersheds")
        layer.add_layer("boundaries",
                         #type="polygon",
                         type="polygon_selector",
                         hover_property="name",
                         line_color="white",
                         line_opacity = 0.5,
                         line_color_selected="dodgerblue",
                         line_opacity_selected  = 1.0,
                         fill_color="dodgerblue",
                         fill_opacity=0.0,
                         fill_color_selected="dodgerblue",
                         fill_opacity_selected=0.3,
                         selection_type="multiple",
                         select=self.select_watershed_from_map
                        )

    def select_watershed_from_map(self, features, layer):
        indices = []
        ids = []
        for feature in features:
            indices.append(feature["properties"]["index"])
            ids.append(feature["properties"]["id"])
        app.gui.setvar("watersheds", "selected_indices", indices)
        app.gui.setvar("watersheds", "selected_ids", ids)    
        app.gui.setvar("watersheds", "nr_selected_watersheds", len(indices))
        app.gui.window.update()

    def update_boundaries_on_map(self):
        dataset_name = app.gui.getvar("watersheds", "dataset")
        dataset = app.watersheds_database.dataset[dataset_name]
        # Get map extent
        extent = app.map.map_extent
        # bbox = [bbox[0][0], bbox[0][1], bbox[1][0], bbox[1][1]]
        xmin = extent[0][0]
        ymin = extent[0][1]
        xmax = extent[1][0]
        ymax = extent[1][1]
        level = app.gui.getvar("watersheds", "level")
        # Waitbox
        wb = app.gui.window.dialog_wait("Loading watersheds ...")
        self.gdf = dataset.get_watersheds_in_bbox(xmin, ymin, xmax, ymax, level)
        app.map.layer["watersheds"].layer["boundaries"].set_data(self.gdf)
        wb.close()

    def select_dataset(self):
        # Update level names
        dataset_name = app.gui.getvar("watersheds", "dataset")
        dataset = app.watersheds_database.dataset[dataset_name]
        app.gui.setvar("watersheds", "level_names", dataset.level_names)
        app.gui.setvar("watersheds", "level_long_names", dataset.level_long_names)
        app.gui.setvar("watersheds", "level", dataset.level_names[0])
        app.gui.setvar("watersheds", "nr_selected_watersheds", 0)
        app.gui.window.update()

    def select_level(self):
        pass

    def save(self):

        if len(self.gdf)==0:
            # No datasets loaded
            return

        dataset_name = app.gui.getvar("watersheds", "dataset")

        if app.map.crs.to_epsg() != 4326:
            crs_string = "_epsg" + str(app.map.crs.to_epsg())
        else:
            crs_string = ""

        # Loop through gdf
        names = []
        ids = []
        polys = []
        for index, row in self.gdf.iterrows():
            if row["id"] in app.gui.getvar("watersheds", "selected_ids"):
                ids.append(row["id"])
                names.append(row["name"])
                # Check if row["geometry"] is a Polygon or MultiPolygon
                if row["geometry"].geom_type == "Polygon":
                    p = Polygon(row["geometry"].exterior.coords)
                    polys.append(p)
                else:
                    # Loop through polygons in MultiPolygon
                    for pol in row["geometry"].geoms:
                        p = Polygon(pol.exterior.coords)
                        polys.append(p)

        if len(names)==0:
            return

        # Get file name from user
        if len(names)>1:
            filename = f"{dataset_name}_merged{crs_string}.geojson"
        else:
            filename = f"{dataset_name}_{ids[0]}{crs_string}.geojson"

        rsp = app.gui.window.dialog_save_file("Save watersheds as ...",
                                            file_name=filename,
                                            filter="*.geojson",
                                            allow_directory_change=False)
        if rsp[0]:
            filename = rsp[2]
        else:
            # User pressed cancel
            return

        # Merge polygons
        merged = unary_union(polys)

        if len(names)>1:
            # Get filename without extension
            filename_txt = os.path.splitext(filename)[0] + ".txt"
            # Write text file with watershed names
            with open(filename_txt, "w") as f:
                for index, name in enumerate(names):
                    f.write(ids[index] + " " + name + '\n')

        # Apply buffer
        self.dbuf = app.gui.getvar("watersheds", "buffer") / 100000.0
        if self.dbuf>0.0:
            merged = merged.buffer(self.dbuf, resolution=16)
            merged = merged.simplify(self.dbuf)

        # Original merged geometry is in WGS84 (because that's what the original data is in)
        # Convert to map crs
        gdf = gpd.GeoDataFrame(geometry=[merged]).set_crs(4326).to_crs(app.map.crs)
        gdf.to_file(filename, driver="GeoJSON")

    def edit_buffer(self):
        pass

# # def get_watersheds_in_bbox(gdb_path, output_path, bbox, layer, name):
# # def get_watersheds_in_bbox(gdb_path, xmin, ymin, xmax, ymax, layer):


# #     # Define the bounding box (xmin, ymin, xmax, ymax)
# #     bounding_box = box(xmin, ymin, xmax, ymax)

# #     # Read the specific layer from the geodatabase
# #     filename = os.path.join(gdb_path, layer + ".shp")
# #     gdf = gpd.read_file(filename)
# #     # gdf = gpd.read_file(gdb_path, layer=layer)

# #     # Filter the data: Keep only multipolygons that intersect with the bounding box
# #     gdf = gdf[gdf.geometry.intersects(bounding_box)]

# #     if layer=="WBDHU2":
# #         hucstr = "huc2"
# #     elif layer=="WBDHU4":
# #         hucstr = "huc4"
# #     elif layer=="WBDHU6":
# #         hucstr = "huc6"
# #     elif layer=="WBDHU8":
# #         hucstr = "huc8"
# #     elif layer=="WBDHU10":
# #         hucstr = "huc10"
# #     elif layer=="WBDHU12":
# #         hucstr = "huc12"
# #     elif layer=="WBDHU14":
# #         hucstr = "huc14"
# #     elif layer=="WBDHU16":
# #         hucstr = "huc16"
    

# #     # # Drop all columns except name, geometry and huc
# #     # gdf = gdf[["name", hucstr, "geometry"]]
# #     # # Rename hucstr to id
# #     gdf = gdf.rename(columns={hucstr: "id"}).to_crs(4326)
    
# #     # fid = open(os.path.join(output_path, name + "_watersheds_" + layer + ".pol"), "w")
    
# #     # for j, watershed in enumerate(watersheds):
# #     #     if watershed.bounds[0]<bbox[2] and watershed.bounds[2]>bbox[0] and watershed.bounds[1]<bbox[3] and watershed.bounds[3]>bbox[1]:
# #     #         gs = watershed.geoms
# #     #         for polygon in gs:
# #     #             crds = polygon.exterior.coords
# #     #             huc = hucs[j]
# #     #             fid.write(huc + "\n")
# #     #             fid.write(str(len(crds)) + ' 2\n')
# #     #             for crd in crds:
# #     #                 lon = crd[0]
# #     #                 lat = crd[1]
# #     #                 fid.write(f'{lon:11.6f}' + ' ' + f'{lat:11.6f}' + '\n')
    
# #     # fid.close()

# #     return gdf

# def create_include_polygon(gdb_path, huc_file, output_path, name, layer="WBDHU8", dbuf=0.0, crs=None):

#     if not output_path:
#         output_path = os.getcwd()

#     if crs:
#         try:
#             # Try epsg code
#             crs = int(crs)            
#         except:
#             pass
#         wgs84 = pyproj.CRS('EPSG:4326')
#         crs1  = pyproj.CRS(crs)
#         if crs1.is_geographic:
#             # Convert metres to degrees
#             dbuf = dbuf / 100000.0
#         # Construct transformer    
#         transformer = pyproj.Transformer.from_crs(wgs84,
#                                                   crs1,
#                                                   always_xy=True).transform

#     # Read list of huc8 IDs    
#     huc_list = []
#     fid = open(huc_file, 'r')
#     lines = fid.readlines()
#     for line in lines:
#         huc_list.append(line.strip())

#     # Read gdb file and make list of polygons
#     gdb_file = os.path.join(gdb_path, "WBD_National_GDB.gdb")
#     source = fiona.open(gdb_file, driver='OpenFileGDB', layer=layer)
#     polys = []
#     wnames = []

#     if layer=="WBDHU2":
#         hucstr = "huc2"
#     elif layer=="WBDHU4":
#         hucstr = "huc4"
#     elif layer=="WBDHU6":
#         hucstr = "huc6"
#     elif layer=="WBDHU8":
#         hucstr = "huc8"
#     elif layer=="WBDHU10":
#         hucstr = "huc10"
#     elif layer=="WBDHU12":
#         hucstr = "huc12"
#     elif layer=="WBDHU14":
#         hucstr = "huc14"
#     elif layer=="WBDHU16":
#         hucstr = "huc16"
    
#     for f in source:
#         if f["properties"][hucstr] in huc_list:
#             print(f["properties"][hucstr])
#             geom = f["geometry"]
#             wnames.append(f["properties"]["name"])
#             for crds in geom["coordinates"]:
#                 p = Polygon(crds[0])
#                 polys.append(p)
#     source.close()    

#     # Merge polygons
#     merged = unary_union(polys)            

#     crsgeo = True
#     if crs:    
#         merged = transform(transformer, merged)        
#         if crs1.is_projected:
#             crsgeo = False

#     # Apply buffer
#     if dbuf>0.0:
#         merged = merged.buffer(dbuf, resolution=16)
#         merged = merged.simplify(dbuf)

#     filename_pol = os.path.join(output_path, name + ".pol")
#     filename_txt = os.path.join(output_path, name + "_watershed_names.txt")

#     # Write text file with watershed names
#     fit = open(filename_txt, "w")
#     for wname in wnames:
#         fit.write(wname + '\n')
#     fit.close()

#     # Write polygon file

#     fid = open(filename_pol, "w")

#     if isinstance(merged, Polygon):

#         crds = merged.exterior.coords
#         fid.write("BL01\n")
#         fid.write(str(len(crds)) + ' 2\n')
#         for crd in crds:
#             lon = crd[0]
#             lat = crd[1]
#             if crsgeo:
#                 fid.write(f'{lon:11.6f}' + ' ' + f'{lat:11.6f}' + '\n')
#             else:
#                 fid.write(f'{lon:11.1f}' + ' ' + f'{lat:11.1f}' + '\n')

#     else:
        
#         for geom in merged.geoms:
#             crds = geom.exterior.coords
#             fid.write("BL01\n")
#             fid.write(str(len(crds)) + ' 2\n')
#             for crd in crds:
#                 lon = crd[0]
#                 lat = crd[1]
#                 if crsgeo:
#                     fid.write(f'{lon:11.6f}' + ' ' + f'{lat:11.6f}' + '\n')
#                 else:
#                     fid.write(f'{lon:11.1f}' + ' ' + f'{lat:11.1f}' + '\n')
            
#     fid.close()
        
#     return merged

def select(*args):
    app.toolbox["watersheds"].select_tab()

def select_dataset(*args):
    app.toolbox["watersheds"].select_dataset()

def select_level(*args):
    app.toolbox["watersheds"].select_level()

def update(*args):
    app.toolbox["watersheds"].update_boundaries_on_map()

def save(*args):
    app.toolbox["watersheds"].save()

def edit_buffer(*args):
    app.toolbox["watersheds"].edit_buffer()
