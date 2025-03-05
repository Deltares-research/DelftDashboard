# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""

from delftdashboard.app import app

def select_dataset(dataset_name):

    # Get dataset to see if it is a COG that has not yet been downloaded
    dataset = app.bathymetry_database.get_dataset(dataset_name)
    if dataset is not None:
        if dataset.format == "cog" and not dataset.path.exists():
            yes = app.gui.window.dialog_yes_no(f"Dataset {dataset.name} is a COG that has not yet been downloaded. Do you want to download it now ?")
            if yes:
                wb = app.gui.window.dialog_wait(f"Downloading dataset {dataset.name} ...")
                print(f"Downloading {dataset.name} from S3")
                print("This may take a while...")
                dataset.download()
                wb.close()
            else:
                app.gui.window.update() # Make sure the new dataset is unchecked
                return

    app.gui.setvar("view_settings", "topography_dataset", dataset_name)
    app.map.layer["main"].layer["background_topography"].update()
    app.gui.setvar("menu", "active_topography_name", dataset_name) # still change this to in menu
    app.gui.window.update() # Make sure the old dataset are unchecked
    
