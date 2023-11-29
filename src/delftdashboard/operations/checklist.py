from pathlib import Path
import yaml


def initialize_checklist():
    checklist_items = [
        "Model boundary",
        "Asset locations",
        "Classification",
        "Damage values",
        "Elevation",
        "Attributes (optional)",
        "Vulnerability",
        "SVI (optional)",
        "Roads (optional)"
    ]
    checklist_items.reverse()  # Reverse because guitares places items from the bottom
    spacing = [10 + (y*20) for y in range(len(checklist_items))]

    # get window config yaml path
    config_path_panel = str(
        Path(Path(__file__).parent.resolve()) / "config" / "checklist_panel.yml"
    )

    with open(config_path_panel) as f:
        # use safe_load instead load
        config_dict = yaml.safe_load(f)

    config_dict["element"] = []
    for i, space in zip(checklist_items, spacing):
        item = {}
        item["style"] = "text"
        item["position"] = {}
        item["position"]["x"] = 25
        item["position"]["y"] = space
        item["position"]["width"] = 100
        item["position"]["height"] = 20
        item["text"] = i
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
    
    return config_dict
