"""GUI callbacks for the bathymetry/topography dataset selector panel.

Handle source selection, dataset add/remove/reorder, z-range editing,
polygon loading, and refresh of the selected-datasets list in the GUI.
"""

from typing import Any

from delftdashboard.app import app


def select_bathymetry_source(*args: Any) -> None:
    """Update the dataset list when the user selects a different source.

    Parameters
    ----------
    *args : Any
        Positional callback arguments; ``args[0]`` is the source name.
    """
    source = args[0]
    dataset_names, dataset_long_names, dataset_source_names = (
        app.topography_data_catalog.dataset_names(source=source)
    )
    group = "bathy_topo_selector"
    app.gui.setvar(group, "bathymetry_dataset_names", dataset_names)
    app.gui.setvar(group, "bathymetry_dataset_index", 0)


def select_bathymetry_dataset(*args: Any) -> None:
    """Handle selection of a dataset in the available-datasets list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """


def use_dataset(*args: Any) -> None:
    """Add the currently highlighted dataset to the selected-datasets list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    group = "bathy_topo_selector"
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    name = names[index]
    if name not in app.gui.getvar(group, "selected_bathymetry_dataset_names"):
        dataset = {"name": name, "elevation": name, "zmin": -99999.0, "zmax": 99999.0}
        app.selected_bathymetry_datasets.append(dataset)
        app.gui.setvar(
            group,
            "selected_bathymetry_dataset_index",
            len(app.selected_bathymetry_datasets) - 1,
        )
        update()


def select_selected_bathymetry_dataset(*args: Any) -> None:
    """Handle selection change in the selected-datasets list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    update()


def remove_selected_bathymetry_dataset(*args: Any) -> None:
    """Remove the currently selected dataset from the selected-datasets list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    if len(app.selected_bathymetry_datasets) == 0:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets.pop(index)
    update()


def move_up_selected_bathymetry_dataset(*args: Any) -> None:
    """Move the currently selected dataset one position up in the list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    if len(app.selected_bathymetry_datasets) < 2:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == 0:
        return
    i0 = index
    i1 = index - 1
    app.selected_bathymetry_datasets[i0], app.selected_bathymetry_datasets[i1] = (
        app.selected_bathymetry_datasets[i1],
        app.selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index - 1)
    update()


def move_down_selected_bathymetry_dataset(*args: Any) -> None:
    """Move the currently selected dataset one position down in the list.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    if len(app.selected_bathymetry_datasets) < 2:
        return
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    if index == len(app.selected_bathymetry_datasets) - 1:
        return
    i0 = index
    i1 = index + 1
    app.selected_bathymetry_datasets[i0], app.selected_bathymetry_datasets[i1] = (
        app.selected_bathymetry_datasets[i1],
        app.selected_bathymetry_datasets[i0],
    )
    app.gui.setvar(group, "selected_bathymetry_dataset_index", index + 1)
    update()


def edit_zmax_bathymetry_dataset(*args: Any) -> None:
    """Update the maximum elevation filter for the selected dataset.

    Parameters
    ----------
    *args : Any
        Positional callback arguments; ``args[0]`` is the new zmax value.
    """
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["zmax"] = args[0]


def edit_zmin_bathymetry_dataset(*args: Any) -> None:
    """Update the minimum elevation filter for the selected dataset.

    Parameters
    ----------
    *args : Any
        Positional callback arguments; ``args[0]`` is the new zmin value.
    """
    group = "bathy_topo_selector"
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["zmin"] = args[0]


def load_polygon(*args: Any) -> None:
    """Load a polygon GeoJSON file and attach it to the selected dataset.

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """
    group = "bathy_topo_selector"
    full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
        "Select polygon file", filter="*.geojson"
    )
    if not full_name:
        return
    index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
    app.selected_bathymetry_datasets[index]["polygon_file"] = full_name


def edit(*args: Any) -> None:
    """Handle the edit action for the selected dataset (not yet implemented).

    Parameters
    ----------
    *args : Any
        Positional callback arguments (unused).
    """


def update() -> None:
    """Refresh the GUI variables for the selected-datasets list."""
    group = "bathy_topo_selector"
    selected_names = []
    nrd = len(app.selected_bathymetry_datasets)
    if nrd > 0:
        for dataset in app.selected_bathymetry_datasets:
            selected_names.append(dataset["name"])
        app.gui.setvar(group, "selected_bathymetry_dataset_names", selected_names)
        index = app.gui.getvar(group, "selected_bathymetry_dataset_index")
        if index > nrd - 1:
            index = nrd - 1
        dataset = app.selected_bathymetry_datasets[index]
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", dataset["zmin"])
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", dataset["zmax"])
    else:
        app.gui.setvar(group, "selected_bathymetry_dataset_names", [])
        app.gui.setvar(group, "selected_bathymetry_dataset_index", 0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmin", -99999.0)
        app.gui.setvar(group, "selected_bathymetry_dataset_zmax", 99999.0)
    app.gui.setvar(group, "nr_selected_bathymetry_datasets", nrd)


def info(*args: Any) -> None:
    """Show the metadata of the currently highlighted dataset in a modal.

    Reads the selection from the available-datasets listbox
    (``bathymetry_dataset_names`` + ``bathymetry_dataset_index``),
    pulls the corresponding ``BathymetryDataset`` from
    ``app.topography_data_catalog``, and pretty-prints its public
    attributes. Container-heavy values (the back-reference to the
    database, the in-memory xr.Dataset cache, dunder keys) are
    filtered out; everything else the catalog loaded from the
    dataset's ``*.tml`` / ``data_catalog.yml`` is shown.
    """
    group = "bathy_topo_selector"
    names = app.gui.getvar(group, "bathymetry_dataset_names")
    if not names:
        app.gui.window.dialog_info("No dataset selected.", title="Dataset info")
        return
    index = app.gui.getvar(group, "bathymetry_dataset_index")
    if index < 0 or index >= len(names):
        app.gui.window.dialog_info("No dataset selected.", title="Dataset info")
        return
    name = names[index]

    try:
        src = app.topography_data_catalog.get_source(name)
    except Exception:
        app.gui.window.dialog_info(
            f"Dataset {name!r} not found in the catalog.",
            title="Dataset info",
        )
        return

    lines: list[str] = []
    # Top-level source attributes worth surfacing.
    for key in ("uri", "data_type", "driver"):
        value = getattr(src, key, None)
        if value is None or value == "":
            continue
        # ``driver`` is a pydantic model on hydromt v1 — show its ``name``.
        driver_name = getattr(value, "name", None)
        if driver_name is not None:
            value = driver_name
        lines.append(f"{key}: {value}")

    # Everything the user / importer put under ``metadata:`` in the YAML.
    metadata = getattr(src, "metadata", None)
    if metadata is not None:
        try:
            md_dict = metadata.model_dump(exclude_none=True)
        except AttributeError:
            md_dict = dict(metadata) if isinstance(metadata, dict) else {}
        for key in sorted(md_dict):
            value = md_dict[key]
            if value is None or value == "":
                continue
            lines.append(f"{key}: {value}")

    text = "\n".join(lines) if lines else "(no metadata available)"
    app.gui.window.dialog_info(text, title=f"Dataset info — {name}")
