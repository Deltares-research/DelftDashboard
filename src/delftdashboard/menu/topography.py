"""Menu callback for selecting the background topography dataset."""

from delftdashboard.app import app


def select_dataset(dataset_name: str) -> None:
    """Switch the background topography to *dataset_name*.

    S3-hosted COG datasets that are not yet available locally require a
    one-time download; the user is asked for confirmation first. On "no" (or
    a failed download) the previously selected dataset remains active.
    """
    size_mb = app.topography_data_catalog.download_required(dataset_name)
    if size_mb is not None:
        ok = app.gui.window.dialog_yes_no(
            f"Dataset {dataset_name} ({size_mb:.0f} MB) is not yet available "
            "locally and needs to be downloaded once. Download now?",
            "Download dataset?",
        )
        if not ok:
            # Revert: nothing was changed yet; refresh the menu so the check
            # mark returns to the previously selected dataset.
            app.gui.window.update()
            return
        dlg = app.gui.window.dialog_wait(
            f"Downloading {dataset_name} ({size_mb:.0f} MB) ... "
            "(progress is printed to the console)"
        )
        success = app.topography_data_catalog.download_dataset(dataset_name)
        dlg.close()
        if not success:
            app.gui.window.dialog_warning(
                f"Downloading dataset {dataset_name} failed. "
                "The previously selected dataset remains active."
            )
            app.gui.window.update()
            return

    app.gui.setvar("view_settings", "topography_dataset", dataset_name)
    app.background_topography_name = dataset_name
    # Drop the DataArray from the previous dataset — the next successful
    # fetch in ``update_background_topography_data`` will replace it.
    # Hover returns "N/A" in the meantime instead of reading stale values.
    app.background_topography = None
    app.map.layer["main"].layer["background_topography"].update()
    app.gui.setvar("menu", "active_topography_name", dataset_name)
    app.gui.window.update()
