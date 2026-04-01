"""Menu callback for selecting the background topography dataset."""

from delftdashboard.app import app


def select_dataset(dataset_name: str) -> None:
    """Switch the background topography to *dataset_name*."""
    app.gui.setvar("view_settings", "topography_dataset", dataset_name)
    app.map.layer["main"].layer["background_topography"].update()
    app.gui.setvar("menu", "active_topography_name", dataset_name)
    app.gui.window.update()
