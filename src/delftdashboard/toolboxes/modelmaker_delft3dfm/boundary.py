"""GUI callbacks for the open boundary tab of the Delft3D-FM model maker toolbox."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the boundary tab and show relevant map layers."""
    map.update()
    app.map.layer[_TB].layer["open_boundary_polygon"].activate()
    # app.map.layer[_TB].layer["outflow_boundary_polygon"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    # app.map.layer[_MODEL].layer["mask"].activate()
    update()


def draw_open_boundary_polygon(*args: Any) -> None:
    """Start interactive drawing of an open boundary polygon."""
    app.map.layer[_TB].layer["open_boundary_polygon"].crs = app.crs
    app.map.layer[_TB].layer["open_boundary_polygon"].draw()
    update()


def delete_open_boundary_polygon(*args: Any) -> None:
    """Delete the currently selected open boundary polygon."""
    if len(app.toolbox[_TB].open_boundary_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "open_boundary_polygon_index")
    app.toolbox[_TB].open_boundary_polygon_names.pop(index)
    feature_id = app.map.layer[_TB].layer["open_boundary_polygon"].get_feature_id(index)
    # Delete from map
    gdf = app.map.layer[_TB].layer["open_boundary_polygon"].delete_feature(feature_id)
    # Delete from app
    app.toolbox[_TB].open_boundary_polygon = app.toolbox[
        _TB
    ].open_boundary_polygon.drop(index)
    if len(app.toolbox[_TB].open_boundary_polygon) > 0:
        app.toolbox[_TB].open_boundary_polygon = app.toolbox[
            _TB
        ].open_boundary_polygon.reset_index(drop=True)
    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox[_TB].open_boundary_polygon) - 1:
        index = max(len(app.toolbox[_TB].open_boundary_polygon) - 1, 0)
        app.gui.setvar(_TB, "open_boundary_polygon_index", index)
    # app.toolbox[_TB].open_boundary_polygon = gdf
    update()


def load_open_boundary_polygon(*args: Any) -> None:
    """Open a file dialog and load open boundary polygons from a file."""
    fname = app.gui.window.dialog_open_file(
        "Select file ...",
        # file_name="coastlines.shp",
        filter=None,  # "*.obs",
        allow_directory_change=True,
        multiple=True,
    )
    app.gui.setvar(_TB, "open_boundary_polygon_file", fname[2])
    app.toolbox[_TB].read_open_boundary_polygon()
    app.toolbox[_TB].plot_open_boundary_polygon()
    update()


def save_open_boundary_polygon(*args: Any) -> None:
    """Save the open boundary polygons to a GeoJSON file."""
    file_name = app.gui.getvar(_TB, "open_boundary_polygon")
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.geojson",
        allow_directory_change=False,
    )
    app.gui.setvar(_TB, "open_boundary_polygon_file", rsp[2])
    app.toolbox[_TB].write_open_boundary_polygon()


def select_open_boundary_polygon(*args: Any) -> None:
    """Activate the polygon feature at the given index on the map.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    app.map.layer[_TB].layer["open_boundary_polygon"].activate_feature(index)


def open_boundary_polygon_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn open boundary polygon and prompt for its name.

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
        name, okay = app.gui.window.dialog_string(
            "Edit name for new open boundary polygon"
        )
        if not okay:
            app.map.layer[_TB].layer["open_boundary_polygon"].delete_feature(index)
            return  # Cancel was clicked
        if name in app.gui.getvar(_TB, "open_boundary_polygon_names"):
            app.gui.window.dialog_info(
                "An open boundary polygon with this name already exists !"
            )
        else:
            break
    gdf.at[index, "name"] = name
    app.toolbox[_TB].open_boundary_polygon = gdf
    nrp = len(app.toolbox[_TB].open_boundary_polygon)
    app.gui.setvar(_TB, "open_boundary_polygon_index", nrp - 1)
    app.toolbox[_TB].open_boundary_polygon_names.append(name)

    update()


def open_boundary_polygon_modified(gdf: Any, index: int, id: Any) -> None:
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
    app.toolbox[_TB].open_boundary_polygon = gdf


def open_boundary_polygon_selected(index: int) -> None:
    """Handle selection of an open boundary polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "open_boundary_polygon_index", index)
    update()


# def edit_resolution(*args):
#     # Get index of selected polygon
#     index = app.gui.getvar(_TB, "refinement_polygon_index")
#     app.toolbox[_TB].refinement_polygon.at[index, "min_edge_size"] = app.gui.getvar(_TB, "ref_min_edge_size")
#     update()

# def draw_outflow_boundary_polygon(*args):
#     app.map.layer[_TB].layer["outflow_boundary_polygon"].crs = app.crs
#     app.map.layer[_TB].layer["outflow_boundary_polygon"].draw()

# def delete_outflow_boundary_polygon(*args):
#     if len(app.toolbox[_TB].outflow_boundary_polygon) == 0:
#         return
#     index = app.gui.getvar(_TB, "outflow_boundary_polygon_index")
#     # Delete from map
#     gdf = app.map.layer[_TB].layer["outflow_boundary_polygon"].delete_feature(index)
#     app.toolbox[_TB].outflow_boundary_polygon = gdf
#     update()

# def load_outflow_boundary_polygon(*args):
#     fname, okay = app.gui.window.dialog_open_file("Select outflow boundary polygon file ...", filter="*.geojson")
#     if not okay:
#         return
#     app.gui.setvar(_TB, "outflow_boundary_polygon_file", fname[2])
#     app.toolbox[_TB].read_outflow_boundary_polygon()
#     app.toolbox[_TB].plot_outflow_boundary_polygon()

# def save_outflow_boundary_polygon(*args):
#     app.toolbox[_TB].write_outflow_boundary_polygon()

# def select_outflow_boundary_polygon(*args):
#     index = args[0]
#     app.map.layer[_TB].layer["outflow_boundary_polygon"].activate_feature(index)

# def outflow_boundary_polygon_created(gdf, index, id):
#     app.toolbox[_TB].outflow_boundary_polygon = gdf
#     nrp = len(app.toolbox[_TB].outflow_boundary_polygon)
#     app.gui.setvar(_TB, "outflow_boundary_polygon_index", nrp - 1)
#     update()

# def outflow_boundary_polygon_modified(gdf, index, id):
#     app.toolbox[_TB].outflow_boundary_polygon = gdf

# def outflow_boundary_polygon_selected(index):
#     app.gui.setvar(_TB, "outflow_boundary_polygon_index", index)
#     update()


def update() -> None:
    """Synchronize the GUI with the current open boundary polygon state."""
    # Open
    index = app.gui.getvar(_TB, "open_boundary_polygon_index")
    nrp = len(app.toolbox[_TB].open_boundary_polygon)
    polnames = app.toolbox[_TB].open_boundary_polygon_names
    app.gui.setvar(_TB, "nr_open_boundary_polygons", nrp)
    app.gui.setvar(_TB, "open_boundary_polygon_names", polnames)
    if index > nrp - 1:
        index = max(nrp - 1, 0)
    app.gui.setvar(_TB, "open_boundary_polygon_index", index)

    # # Outflow
    # nrp = len(app.toolbox[_TB].outflow_boundary_polygon)
    # names = []
    # for ip in range(nrp):
    #     names.append(str(ip + 1))
    # app.gui.setvar(_TB, "nr_outflow_boundary_polygons", nrp)
    # app.gui.setvar(_TB, "outflow_boundary_polygon_names", names)
    # index = app.gui.getvar(_TB, "outflow_boundary_polygon_index")
    # if index > nrp - 1:
    #     index = max(nrp - 1, 0)
    # app.gui.setvar(_TB, "outflow_boundary_polygon_index", index)

    # Update GUI
    app.gui.window.update()


def generate_bnd_coastline(*args: Any) -> None:
    """Generate open boundary points based on the coastline."""
    app.toolbox[_TB].generate_bnd_coastline()


def generate_bnd_polygon(*args: Any) -> None:
    """Generate open boundary points based on the drawn polygon."""
    app.toolbox[_TB].generate_bnd_polygon()


def load_bnd(*args: Any) -> None:
    """Open a file dialog and load boundary points from a .pli file."""
    fname = app.gui.window.dialog_open_file(
        "Select file ...",
        file_name="bnd.pli",
        filter="*.pli",
        allow_directory_change=True,
    )
    app.toolbox[_TB].load_bnd(fname[0])


def set_resolution(*args: Any) -> None:
    """Update the boundary resolution from current GUI values."""
    update()


# def update_mask(*args):
#     app.toolbox[_TB].update_mask()

# def cut_inactive_cells(*args):
#     app.toolbox[_TB].cut_inactive_cells()
