"""Menu callback for selecting the background topography dataset."""

from delftdashboard.app import app


def select_dataset(dataset_name: str) -> None:
    """Switch the background topography to *dataset_name*."""
    app.gui.setvar("view_settings", "topography_dataset", dataset_name)
    app.background_topography_name = dataset_name
    # Drop the DataArray from the previous dataset — the next successful
    # fetch in ``update_background_topography_data`` will replace it.
    # Hover returns "N/A" in the meantime instead of reading stale values.
    app.background_topography = None
    app.map.layer["main"].layer["background_topography"].update()
    app.gui.setvar("menu", "active_topography_name", dataset_name)
    app.gui.window.update()
