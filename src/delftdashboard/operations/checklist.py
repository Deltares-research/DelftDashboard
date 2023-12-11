from pathlib import Path
import yaml

from delftdashboard.app import app


def initialize_checklist():
    checklist_items = [
        "Model boundary",
        "Asset locations",
        "Classification",
        "Damage values",
        "Finished floor height",
        "Vulnerability",
        "SVI (optional)",
        "Roads (optional)",
        "Attributes (optional)",
    ]
    checklist_items.reverse()  # Reverse because guitares places items from the bottom
    spacing = [5 + (y*20) for y in range(len(checklist_items))]

    # get window config yaml path
    config_path_panel = str(
        Path(Path(__file__).parent.resolve()) / "config" / "checklist_panel.yml"
    )

    with open(config_path_panel) as f:
        # use safe_load instead load
        config_dict = yaml.safe_load(f)

    # Add a header
    config_dict["element"] = []
    item = {}
    item["style"] = "text"
    item["position"] = {}
    item["position"]["x"] = 10
    item["position"]["y"] = max(spacing) + 23
    item["position"]["width"] = 100
    item["position"]["height"] = 15
    item["text"] = "<u><b>Model parameters</b></u>"
    config_dict["element"].append(item)

    for i, space in zip(checklist_items, spacing):
        item = {}
        item["style"] = "text"
        item["position"] = {}
        item["position"]["x"] = 25
        item["position"]["y"] = space
        item["position"]["width"] = 100
        item["position"]["height"] = 20
        if i.endswith("(optional)"):
            text = "<i>" + i + "</i>"
        else:
            text = i
        item["text"] = text
        config_dict["element"].append(item)

        # The empty ballot box
        item = {}
        item["style"] = "text"
        item["position"] = {}
        item["position"]["x"] = 10
        item["position"]["y"] = space + 5
        item["position"]["width"] = 8
        item["position"]["height"] = 8
        item["text"] = "\u2610"
        
        dependency = {}
        dependency["action"] = "visible"
        dependency["checkfor"] = "all"
        
        check = {}
        check["variable"] = "checkbox" + "_" + i.lower().replace(" ", "_")
        check["operator"] = "eq"
        check["value"] = False
        
        dependency["check"] = [check]
        item["dependency"] = [dependency]

        config_dict["element"].append(item)

        # The checked ballot box
        item = {}
        item["style"] = "text"
        item["position"] = {}
        item["position"]["x"] = 10
        item["position"]["y"] = space + 6
        item["position"]["width"] = 8
        item["position"]["height"] = 8
        item["text"] = "\u2611"
        
        dependency = {}
        dependency["action"] = "visible"
        dependency["checkfor"] = "all"
        
        check = {}
        check["variable"] = "checkbox" + "_" + i.lower().replace(" ", "_")
        check["operator"] = "eq"
        check["value"] = True

        dependency["check"] = [check]
        item["dependency"] = [dependency]

        config_dict["element"].append(item)
    
        if i == 'Model boundary':
            # Add the zoom to boundary button
            item = {}
            item["style"] = "pushbutton"
            item["position"] = {}
            item["position"]["x"] = 90
            item["position"]["y"] = space
            item["position"]["width"] = 16
            item["position"]["height"] = 16
            item["text"] = "\u233E"
            item["method"] = "zoom_to_boundary"
            config_dict["element"].append(item)

    return config_dict


def zoom_to_boundary(*args):
    active_layer = app.gui.getvar("modelmaker_fiat", "active_area_of_interest")
    if active_layer:
        gdf = app.active_toolbox.area_of_interest

        # get the aoi bounds
        bounds = gdf.geometry.bounds

        # Fly to the site
        app.map.fit_bounds(
            bounds.minx[0], bounds.miny[0], bounds.maxx[0], bounds.maxy[0]
        )
    else:
        app.gui.window.dialog_info(
            text="Please first select a model boundary.",
            title="No model boundary selected",
        )