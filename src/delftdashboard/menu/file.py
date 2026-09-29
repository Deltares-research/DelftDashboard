"""Menu callbacks for File menu actions (new, open, save, exit)."""

import os
from pathlib import Path

from delftdashboard.app import app


def new(option: str) -> None:
    """Reset all models and toolboxes to their initial state.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    ok = app.gui.window.dialog_yes_no("This will clear all existing data! Continue?")
    if not ok:
        return

    # Initialize toolboxes
    for toolbox in app.toolbox.values():
        toolbox.initialize()
        toolbox.clear_layers()

    # Initialize models
    for model in app.model.values():
        model.initialize()
        model.clear_layers()

    # app.active_model   = app.model[list(app.model)[0]]
    # app.active_toolbox = app.toolbox[list(app.toolbox)[0]]
    app.active_toolbox.select()


def open(option: str) -> None:
    """Open a model from file via the active model's open method.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    app.active_model.open()


def save(option: str) -> None:
    """Save the active model to file.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    app.active_model.save()


def select_working_directory(option: str) -> None:
    """Prompt the user to select a new working directory and apply it.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    path = app.gui.window.dialog_select_path(
        "Select working directory ...", path=os.getcwd()
    )
    if path:
        os.chdir(path)
        # Remember this choice so the next startup returns to it.
        from delftdashboard.operations.initialize import save_working_directory

        save_working_directory(path)
        # Set path for all models to new working directory
        for model in app.model:
            try:
                set_model_path(app.model[model].domain, path)
            except Exception as e:
                print(f"Could not set path for model {model}: {e}")


def set_model_path(domain, path: str) -> None:
    """Point a model's domain at a new folder.

    HydroMT-based models (sfincs_hmt, hurrywave_hmt) keep their location in
    ``domain.root``, a ``ModelRoot`` that resolved ``root="."`` to an absolute
    path when the model was created. Changing the working directory therefore
    has no effect on where they write unless the root is updated too. The cht
    based models simply hold a ``path`` attribute.

    The ``ModelRoot.path`` setter is deliberately bypassed: it removes the
    previous root folder when that folder is empty, and a working-directory
    switch must never delete a user's folder.
    """
    root = getattr(domain, "root", None)
    if root is not None and hasattr(root, "_path"):
        root._path = Path(path).resolve()
    else:
        domain.path = path


def exit(option: str) -> None:
    """Quit the application.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    app.gui.quit()
