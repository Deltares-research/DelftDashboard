"""GUI callbacks for the bathymetry tab of the Delft3D-FM model maker toolbox."""

from typing import Any, List

from delftdashboard.app import app
from delftdashboard.operations import map

_TB = "modelmaker_delft3dfm"
_MODEL = "delft3dfm"


def select(*args: Any) -> None:
    """Activate the bathymetry tab and show the grid layer."""
    map.update()
    app.map.layer[_MODEL].layer["grid"].show()


def select_bathymetry_source(*args: Any) -> None:
    """Update the dataset list when the user selects a bathymetry source.

    Parameters
    ----------
    *args : Any
        First element is the selected source name.
    """
    source = args[0]
    dataset_names, dataset_long_names, dataset_source_names = (
        app.topography_data_catalog.dataset_names(source=source)
    )
    app.gui.setvar(_TB, "bathymetry_dataset_names", dataset_names)
    app.gui.setvar(_TB, "bathymetry_dataset_index", 0)


def select_bathymetry_dataset(*args: Any) -> None:
    """Handle selection of a bathymetry dataset in the available list."""
    pass


def use_dataset(*args: Any) -> None:
    """Add the currently selected bathymetry dataset to the active list."""
    group = _TB
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    name = names[index]
    if name not in app.gui.getvar(group, "selected_bathymetry_dataset_names"):
        dataset = {"name": name, "zmin": -99999.0, "zmax": 99999.0}
        app.toolbox[_TB].selected_bathymetry_datasets.append(dataset)
        app.gui.setvar(
            group,
            "selected_bathymetry_dataset_index",
            len(app.toolbox[_TB].selected_bathymetry_datasets) - 1,
        )
        update()


def select_selected_bathymetry_dataset(*args: Any) -> None:
    """Handle selection of a dataset in the selected-datasets list."""
    update()


def remove_selected_bathymetry_dataset(*args: Any) -> None:
    """Remove the currently selected bathymetry dataset from the active list."""
    if len(app.toolbox[_TB].selected_bathymetry_datasets) == 0:
        return
    group = _TB
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox[_TB].selected_bathymetry_datasets.pop(index)
    update()


def move_up_selected_bathymetry_dataset(*args: Any) -> None:
    """Move the selected bathymetry dataset one position up in the list."""
    if len(app.toolbox[_TB].selected_bathymetry_datasets) < 2:
        return
    group = _TB
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    (
        app.toolbox[_TB].selected_bathymetry_datasets[i0],
        app.toolbox[_TB].selected_bathymetry_datasets[i1],
    ) = (
        app.toolbox[_TB].selected_bathymetry_datasets[i1],
        app.toolbox[_TB].selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args: Any) -> None:
    """Move the selected bathymetry dataset one position down in the list."""
    if len(app.toolbox[_TB].selected_bathymetry_datasets) < 2:
        return
    group = _TB
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == len(app.toolbox[_TB].selected_bathymetry_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    (
        app.toolbox[_TB].selected_bathymetry_datasets[i0],
        app.toolbox[_TB].selected_bathymetry_datasets[i1],
    ) = (
        app.toolbox[_TB].selected_bathymetry_datasets[i1],
        app.toolbox[_TB].selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()


def edit_zmax_bathymetry_dataset(*args: Any) -> None:
    """Update the zmax value for the selected bathymetry dataset.

    Parameters
    ----------
    *args : Any
        First element is the new zmax value.
    """
    group = _TB
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox[_TB].selected_bathymetry_datasets[index]["zmax"] = args[0]


def edit_zmin_bathymetry_dataset(*args: Any) -> None:
    """Update the zmin value for the selected bathymetry dataset.

    Parameters
    ----------
    *args : Any
        First element is the new zmin value.
    """
    group = _TB
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.toolbox[_TB].selected_bathymetry_datasets[index]["zmin"] = args[0]


def update() -> None:
    """Synchronize the GUI with the current selected bathymetry dataset state."""
    group = _TB
    selected_names: List[str] = []
    nrd = len(app.toolbox[_TB].selected_bathymetry_datasets)
    if nrd > 0:
        for dataset in app.toolbox[_TB].selected_bathymetry_datasets:
            selected_names.append(dataset["name"])
        app.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.toolbox[_TB].selected_bathymetry_datasets[index]
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
    else:
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)


def generate_bathymetry(*args: Any) -> None:
    """Generate bathymetry for the Delft3D-FM grid."""
    app.toolbox[_TB].generate_bathymetry()


def info(*args: Any) -> None:
    """Display information about the selected bathymetry dataset."""
    pass
