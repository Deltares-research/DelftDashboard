"""Menu callbacks for the Help menu."""

import webbrowser

from delftdashboard.app import app


def toggle_documentation(*args) -> None:
    """Toggle the documentation panel visibility."""
    app.gui.collapse("dual")


def open_documentation(*args) -> None:
    """Open the DelftDashboard documentation in the browser."""
    webbrowser.open("https://delftdashboard.readthedocs.io/en/latest/")


def open_deltares_website(*args) -> None:
    """Open the Deltares website in the browser."""
    webbrowser.open("https://www.deltares.nl/")


def open_sfincs_website(*args) -> None:
    """Open the SFINCS documentation website in the browser."""
    webbrowser.open("https://sfincs.readthedocs.io/en/latest/")


def open_issue_tracker(*args) -> None:
    """Open the GitHub issue tracker in the browser."""
    webbrowser.open("https://github.com/Deltares-research/DelftDashboard/issues")


def about(*args) -> None:
    """Show the About dialog."""
    import delftdashboard

    version = getattr(delftdashboard, "__version__", "0.0.1")
    app.gui.window.dialog_info(
        f"DelftDashboard v{version}\n\n"
        "A desktop application for setting up and visualizing\n"
        "coastal and hydraulic numerical models.\n\n"
        "Developed by Deltares\n"
        "https://www.deltares.nl/",
        "About DelftDashboard",
    )
