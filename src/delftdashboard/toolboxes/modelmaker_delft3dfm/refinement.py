"""GUI callbacks for the grid refinement tab of the Delft3D-FM model maker toolbox."""

from typing import Any

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the refinement tab and show relevant map layers."""
    map.update()
    app.map.layer[_TB].layer["polygon_refinement"].activate()
    app.map.layer[_MODEL].layer["grid"].activate()
    app.map.layer[_TB].layer["grid_outline"].activate()
    update()


def draw_refinement_polygon(*args: Any) -> None:
    """Start interactive drawing of a refinement polygon on the map."""
    app.map.layer[_TB].layer["polygon_refinement"].crs = app.crs
    app.map.layer[_TB].layer["polygon_refinement"].draw()
    update()


def delete_refinement_polygon(*args: Any) -> None:
    """Delete the currently selected refinement polygon."""
    if len(app.toolbox[_TB].refinement_polygon) == 0:
        return
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon_names.pop(index)
    feature_id = app.map.layer[_TB].layer["polygon_refinement"].get_feature_id(index)
    # Delete from map
    app.map.layer[_TB].layer["polygon_refinement"].delete_feature(feature_id)
    # Delete from app
    app.toolbox[_TB].refinement_polygon = app.toolbox[_TB].refinement_polygon.drop(
        index
    )
    if len(app.toolbox[_TB].refinement_polygon) > 0:
        app.toolbox[_TB].refinement_polygon = app.toolbox[
            _TB
        ].refinement_polygon.reset_index(drop=True)

    # If the last polygon was deleted, set index to last available polygon
    if index > len(app.toolbox[_TB].refinement_polygon) - 1:
        index = max(len(app.toolbox[_TB].refinement_polygon) - 1, 0)
        app.gui.setvar(_TB, "refinement_polygon_index", index)
    update()


def load_refinement_polygon(*args: Any) -> None:
    """Open a file dialog and load refinement polygons from a GeoJSON file."""
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select refinement polygon file ...", filter="*.geojson"
    )
    if not full_name:
        return
    app.gui.setvar(_TB, "refinement_polygon_file", full_name)
    app.toolbox[_TB].read_refinement_polygon()
    app.toolbox[_TB].plot_refinement_polygon()
    update()


def save_refinement_polygon(*args: Any) -> None:
    """Save the refinement polygons to a GeoJSON file."""
    file_name = app.gui.getvar(_TB, "refinement_polygon_file")
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=file_name,
        filter="*.geojson",
        allow_directory_change=False,
    )
    app.gui.setvar(_TB, "refinement_polygon_file", rsp[2])
    app.toolbox[_TB].write_refinement_polygon()


def select_refinement_polygon(*args: Any) -> None:
    """Activate the refinement polygon feature at the given index on the map.

    Parameters
    ----------
    *args : Any
        First element is the polygon index.
    """
    index = args[0]
    #    feature_id = app.map.layer[_TB].layer["polygon_refinement"].get_feature_id(index)
    #    feature_id = app.toolbox[_TB].refinement_polygon.loc[index, "id"]
    app.map.layer[_TB].layer["polygon_refinement"].activate_feature(index)


# def select_refinement_level(*args):
#     level_index = args[0]
#     # Get index of selected polygon
#     index = app.gui.getvar(_TB, "refinement_polygon_index")
#     app.toolbox[_TB].refinement_levels[index] = level_index + 1
#     update()


def edit_settings(*args: Any) -> None:
    """Apply edited refinement settings to the selected polygon."""
    # Get index of selected polygon
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    app.toolbox[_TB].refinement_polygon.at[index, "min_edge_size"] = app.gui.getvar(
        _TB, "ref_min_edge_size"
    )
    update()


def refinement_polygon_created(gdf: Any, index: int, id: Any) -> None:
    """Store a newly drawn refinement polygon and prompt for its name.

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
            "Edit name for new refinement polygon"
        )
        if not okay:
            app.map.layer[_TB].layer["polygon_refinement"].delete_feature(index)
            return  # Cancel was clicked
        if name in app.gui.getvar(_TB, "refinement_polygon_names"):
            app.gui.window.dialog_info(
                "A refinement polygon with this name already exists !"
            )
        else:
            break
    app.toolbox[_TB].refinement_polygon = gdf
    nrp = len(app.toolbox[_TB].refinement_polygon)
    app.gui.setvar(_TB, "refinement_polygon_index", nrp - 1)
    # # Add refinement polygon name
    app.toolbox[_TB].refinement_polygon_names.append(name)
    update()


def refinement_polygon_modified(gdf: Any, index: int, id: Any) -> None:
    """Update the stored refinement polygon after the user modifies it.

    Parameters
    ----------
    gdf : GeoDataFrame
        The modified GeoDataFrame.
    index : int
        Index of the modified feature.
    id : Any
        Feature identifier.
    """
    app.toolbox[_TB].refinement_polygon = gdf


def refinement_polygon_selected(index: int) -> None:
    """Handle selection of a refinement polygon on the map.

    Parameters
    ----------
    index : int
        Index of the selected polygon.
    """
    app.gui.setvar(_TB, "refinement_polygon_index", index)
    update()


def update() -> None:
    """Synchronize the GUI with the current refinement polygon state."""
    index = app.gui.getvar(_TB, "refinement_polygon_index")
    # levels = app.toolbox[_TB].refinement_levels
    # if len(levels) > 0:
    #     app.gui.setvar(_TB, "refinement_polygon_level", levels[index] - 1)
    # else:
    #     app.gui.setvar(_TB, "refinement_polygon_level", 0)
    nrp = len(app.toolbox[_TB].refinement_polygon)
    if nrp > 0:
        min_edge_size = app.toolbox[_TB].refinement_polygon.loc[index, "min_edge_size"]
        app.gui.setvar(_TB, "ref_min_edge_size", min_edge_size)
    else:
        app.gui.setvar(_TB, "ref_min_edge_size", 0)
    # refnames = []
    # levstr = app.gui.getvar(_TB, "refinement_polygon_levels")
    # if nrp>0:
    #     for ip in range(nrp):
    #         refnames.append(str(ip + 1) + " (" + levstr[levels[ip] - 1] + ")")
    # else:
    #     pass
    refnames = app.toolbox[_TB].refinement_polygon_names
    app.gui.setvar(_TB, "nr_refinement_polygons", nrp)
    app.gui.setvar(_TB, "refinement_polygon_names", refnames)
    app.gui.window.update()


def build_depthrefined_grid(*args: Any) -> None:
    """Generate a depth-refined grid."""
    app.toolbox[_TB].generate_depth_refinement()


def build_polygonrefined_grid(*args: Any) -> None:
    """Generate a polygon-refined grid."""
    app.toolbox[_TB].generate_polygon_refinement()


def build_polygondepthrefined_grid(*args: Any) -> None:
    """Generate a combined polygon-and-depth-refined grid."""
    app.toolbox[_TB].generate_polygon_depth_refinement()


def connect_nodes(*args: Any) -> None:
    """Connect hanging nodes in the grid."""
    app.toolbox[_TB].connect_nodes()


def refine_size(*args: Any) -> None:
    """Set the minimum edge size for depth-based refinement from GUI values."""
    # app.model[_MODEL].domain.grid.refinement_polygon= app.toolbox[_TB, "refinement_polygon")
    # app.model[_MODEL].domain.refinement_depth= app.gui.getvar(_TB, "refinement_depth")
    app.model[_MODEL].domain.grid.min_edge_size = app.gui.getvar(
        _TB, "depth_min_edge_size"
    )
