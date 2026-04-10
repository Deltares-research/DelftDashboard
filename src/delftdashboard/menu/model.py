"""Menu callbacks for switching the active model."""

from delftdashboard.operations.model import select_model


def select(model_name: str) -> None:
    """Select and activate a model by name.

    Parameters
    ----------
    model_name : str
        Name of the model to select.
    """
    select_model(model_name)
