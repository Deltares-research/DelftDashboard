from delftdashboard.app import app

def select_crs(*args):
    pass

def edit_search_string(*args):

    filtered_names = app.gui.getvar("select_other_projected", "filtered_names")
    search_string = app.gui.getvar("select_other_projected", "search_string")
    search_string = search_string.strip()

    if len(search_string) == 0:
        app.gui.setvar("select_other_projected", "filtered_names",
                       app.gui.getvar("select_other_projected", "crs_names"))
        return
    else:
        # Find all names that contain the search string
        filtered_names = []
        for name in app.gui.getvar("select_other_projected", "crs_names"):
            if search_string.lower() in name.lower():
                filtered_names.append(name)
        app.gui.setvar("select_other_projected", "filtered_names", filtered_names)
        app.gui.setvar("select_other_projected", "crs_index", 0)

    app.gui.popup_window["select_other_projected"].update()
