"""Menu callbacks for File menu actions (new, open, save, exit)."""

import os

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
        # Set path for all models to new working directory
        for model in app.model:
            try:
                app.model[model].domain.path = path
            except Exception:
                print("Could not set path for model : ", model)
                pass


def exit(option: str) -> None:
    """Quit the application.

    Parameters
    ----------
    option : str
        Menu option identifier (unused).
    """
    app.gui.quit()
