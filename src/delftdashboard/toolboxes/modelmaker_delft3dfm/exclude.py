"""GUI callbacks for the exclude-polygon tab of the Delft3D-FM model maker toolbox."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the exclude tab and show relevant map layers."""
    map.update()
    # Show the mask include and exclude polygons
    # app.map.layer[_TB].layer["include_polygon"].activate()
    app.map.layer[_TB].layer["exclude_polygon"].activate()
    # Show the grid and mask
    app.map.layer["sfincs_cht"].layer["grid"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_include"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_open_boundary"].activate()
    # app.map.layer["sfincs_cht"].layer["mask_outflow_boundary"].activate()
    update()


# def draw_include_polygon(*args):
#     app.map.layer[_TB].layer["include_polygon"].crs = app.crs
#     app.map.layer[_TB].layer["include_polygon"].draw()

# def delete_include_polygon(*args):
#     if len(app.toolbox[_TB].include_polygon) == 0:
#         return
#     index = app.gui.getvar(_TB, "include_polygon_index")
#     gdf = app.map.layer[_TB].layer["include_polygon"].delete_feature(index)
#     app.toolbox[_TB].include_polygon = gdf
#     update()

# def load_include_polygon(*args):
#     full_name, path, name, ext, fltr = app.gui.window.dialog_open_file("Select include polygon file ...", filter="*.geojson")
#     okay = True
#     if not okay:
#         return
#     app.gui.setvar(_TB, "include_polygon_file", name)
#     app.toolbox[_TB].read_include_polygon()
#     app.toolbox[_TB].plot_include_polygon()
#     update()

# def save_include_polygon(*args):
#     app.toolbox[_TB].write_include_polygon()

# def select_include_polygon(*args):
#     index = args[0]
#     app.map.layer[_TB].layer["include_polygon"].activate_feature(index)

# def include_polygon_created(gdf, index, id):
#     app.toolbox[_TB].include_polygon = gdf
#     nrp = len(app.toolbox[_TB].include_polygon)
#     app.gui.setvar(_TB, "include_polygon_index", nrp - 1)
#     update()

# def include_polygon_modified(gdf, index, id):
#     app.toolbox[_TB].include_polygon = gdf

# def include_polygon_selected(index):
#     # Selected from map
#     app.gui.setvar(_TB, "include_polygon_index", index)
#     update()


def draw_exclude_polygon(*args: Any) -> None:
    """Start interactive drawing of an exclude polygon on the map."""
    app.map.layer[_TB].layer["exclude_polygon"].crs = app.crs
    app.map.layer[_TB].layer["exclude_polygon"].draw()
    update()


def delete_exclude_polygon(*args: Any) -> None:
    """Delete the currently selected exclude polygon."""
    if len(app.toolbox[_TB].exclude_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    app.toolbox[_TB].exclude_polygon_names.pop(index)
    feature_id = app.map.layer[_TB].layer["exclude_polygon"].get_feature_id(index)
    # Delete from map
    gdf = app.map.layer[_TB].layer["exclude_polygon"].delete_feature(feature_id)
    # Delete from app
    app.toolbox[_TB].exclude_polygon = app.toolbox[_TB].exclude_polygon.drop(index)
    if len(app.toolbox[_TB].exclude_polygon) > 0:
        app.toolbox[_TB].exclude_polygon = app.toolbox[_TB].exclude_polygon.reset_index(
            drop=True
        )
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox[_TB].exclude_polygon) - 1:
        index = max(len(app.toolbox[_TB].exclude_polygon) - 1, 0)
        app.gui.setvar(_TB, "exclude_polygon_index", index)
    # app.toolbox[_TB].exclude_polygon = gdf
    update()


def load_exclude_polygon(*args: Any) -> None:
    """Open a file dialog and load exclude polygons from a file."""
    fname = app.gui.window.dialog_open_file(
        "Select file ...",
        # file_name="coastlines.shp",
        filter=None,  # "*.obs",
        allow_directory_change=True,
        multiple=True,
    )
    app.gui.setvar(_TB, "exclude_polygon_file", fname[2])
    app.toolbox[_TB].read_exclude_polygon()
    app.toolbox[_TB].plot_exclude_polygon()
    update()


def save_exclude_polygon(*args: Any) -> None:
    """Save the exclude polygons to a GeoJSON file."""
    file_name = app.gui.getvar(_TB, "exclude_polygon")
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.geojson",
        allow_directory_change=False,
    )
    app.gui.setvar(_TB, "exclude_polygon_file", rsp[2])
    app.toolbox[_TB].write_exclude_polygon()


def select_exclude_polygon(*args: Any) -> None:
    """Activate the exclude polygon feature at the given index on the map.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["exclude_polygon"].activate_feature(index)


def exclude_polygon_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn exclude polygon and prompt for its name.

    Parameters
    ----------
    gdf : GeoDataFrame
        The GeoDataFrame containing the drawn polygons.
    index : int
        Index of the created feature.
    id : Any
        Feature identifier.
    """
    while True:
        name, okay = app.gui.window.dialog_string("Edit name for new exclude polygon")
        if not okay:
            app.map.layer[_TB].layer["exclude_polygon"].delete_feature(index)
            return
        if name:
            break
    app.toolbox[_TB].exclude_polygon = gdf
    nrp = len(app.toolbox[_TB].exclude_polygon)
    app.gui.setvar(_TB, "exclude_polygon_index", nrp - 1)
    app.toolbox[_TB].exclude_polygon_names.append(name)
    update()


def exclude_polygon_modified(gdf: Any, index: int, id: Any) -> None:
    """Update the stored polygon after the user modifies it on the map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].exclude_polygon = gdf


def exclude_polygon_selected(index: int) -> None:
    """Handle selection of an exclude polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    update()


def update() -> None:
    """Synchronize the GUI with the current exclude polygon state."""
    # Include
    # nrp = len(app.toolbox[_TB].include_polygon)
    # incnames = []
    # for ip in range(nrp):
    #     incnames.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_include_polygons", nrp)
    # app.gui.setvar(_TB, "include_polygon_names", incnames)
    # index = app.gui.getvar(_TB, "include_polygon_index")
    # if index > nrp - 1:
    #     index = max(nrp - 1, 0)
    # app.gui.setvar(_TB, "include_polygon_index", index)

    # Exclude
    index = app.gui.getvar(_TB, "exclude_polygon_index")
    nrp = len(app.toolbox[_TB].exclude_polygon)
    excnames = app.toolbox[_TB].exclude_polygon_names
    app.gui.setvar(_TB, "nr_exclude_polygons", nrp)
    app.gui.setvar(_TB, "exclude_polygon_names", excnames)
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "exclude_polygon_index", index)
    # Update GUI
    app.gui.window.update()


def update_mask(*args: Any) -> None:
    """Update the active cell mask based on current polygons."""
    app.toolbox[_TB].update_mask()


def cut_polygon(*args: Any) -> None:
    """Cut grid cells using the exclude polygons."""
    app.toolbox[_TB].cut_polygon()


def cut_coastline(*args: Any) -> None:
    """Cut grid cells using the coastline."""
    app.toolbox[_TB].cut_coastline()
