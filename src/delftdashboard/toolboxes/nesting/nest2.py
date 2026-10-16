"""GUI callbacks for nesting step 2: extract boundary conditions from the overall model output."""

from __future__ import annotations

import os
from typing import Any

from cht_hurrywave import HurryWave
from cht_nesting import nest2
from cht_sfincs import SFINCS

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the nest-2 tab and reset overall model state.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.update()
    # Set detail model loaded to False to avoid confusion
    app.gui.setvar("nesting", "overall_model_type", "")
    app.gui.setvar("nesting", "overall_model_loaded", False)
    update()


def update(*args: Any) -> None:
    """Refresh the list of available overall model types for the active model.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    # Set the overall model names
    if app.active_model.name == "sfincs_cht":
        # Check if waves are turned on
        if app.active_model.domain.input.variables.snapwave:
            overall_model_types = ["sfincs_cht", "delft3dfm", "hurrywave"]
        else:
            overall_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "sfincs_hmt":
        overall_model_types = ["sfincs_hmt", "hurrywave_hmt"]
    elif app.active_model.name == "delft3dfm":
        overall_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "hurrywave":
        overall_model_types = ["hurrywave"]
    elif app.active_model.name == "hurrywave_hmt":
        overall_model_types = ["hurrywave_hmt"]
    else:
        overall_model_types = []

    # Drop any types that aren't actually loaded as models in this session.
    overall_model_types = [t for t in overall_model_types if t in app.model]
    app.gui.setvar("nesting", "overall_model_types", overall_model_types)

    # Check if the current model name is in the overall model names. If the
    # list is empty (no compatible overall model loaded) leave the var alone.
    overall_model_type = app.gui.getvar("nesting", "overall_model_type")
    if overall_model_types and overall_model_type not in overall_model_types:
        app.gui.setvar(
            "nesting",
            "overall_model_type",
            overall_model_types[0],
        )

    # Set the overall model long names
    long_names = [app.model[m].long_name for m in overall_model_types]
    app.gui.setvar("nesting", "overall_model_type_long_names", long_names)

    app.gui.window.update()


def load_overall_model(*args: Any) -> None:
    """Open a file dialog and load the overall model input file.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    overall_model_type = app.gui.getvar("nesting", "overall_model_type")

    if overall_model_type == "sfincs_cht":
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="sfincs.inp",
            filter="sfincs.inp",
            allow_directory_change=True,
        )
    elif overall_model_type in ("hurrywave", "hurrywave_hmt"):
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="hurrywave.inp",
            filter="hurrywave.inp",
            allow_directory_change=True,
        )
    elif overall_model_type == "sfincs_hmt":
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="sfincs.inp",
            filter="sfincs.inp",
            allow_directory_change=True,
        )
    else:
        # This should never happen
        print("Unknown overall model name: ", overall_model_type)
        return

    if rsp[0]:
        app.gui.setvar("nesting", "overall_model_file", rsp[0])
        app.gui.setvar("nesting", "overall_model_loaded", True)
    else:
        app.gui.setvar("nesting", "overall_model_file", "")
        app.gui.setvar("nesting", "overall_model_loaded", False)
        return


def select_overall_model_type(*args: Any) -> None:
    """Reset the loaded state when the overall model type changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.gui.setvar("nesting", "overall_model_loaded", False)


def edit_obs_point_prefix(*args: Any) -> None:
    """Handle edits to the observation point prefix (no-op placeholder).

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    pass


def edit_water_level_correction(*args: Any) -> None:
    """Handle edits to the water level correction (no-op placeholder).

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    pass


def perform_nesting_step_2(*args: Any) -> None:
    """Execute nesting step 2: extract boundary conditions from overall model output.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    overall_model_type = app.gui.getvar("nesting", "overall_model_type")
    overall_model_file = app.gui.getvar("nesting", "overall_model_file")

    if app.active_model.name in ("sfincs_hmt", "hurrywave_hmt"):
        _perform_nesting_step_2_hmt(overall_model_type, overall_model_file)
        return

    if app.active_model.name == "sfincs_cht":
        if overall_model_type == "hurrywave":
            # SnapWave boundary conditions (don't ask for filenames in this case)
            pass

        else:
            # Points were only added to the sfincs_cht model. Need to know new file name.
            file_name = app.model["sfincs_cht"].domain.input.variables.bzsfile
            if not file_name:
                file_name = "sfincs.bzs"
            rsp = app.gui.window.dialog_save_file(
                "Select file ...",
                file_name=file_name,
                filter="*.bzs",
                allow_directory_change=False,
            )
            if rsp[0]:
                bzsfile = rsp[2]  # file name without path
            else:
                return

    elif app.active_model.name == "hurrywave":
        # Points were only added to the sfincs_cht model. Need to know new file name.
        file_name = app.model["hurrywave"].domain.input.variables.bspfile
        if not file_name:
            file_name = "hurrywave.bsp"
        rsp = app.gui.window.dialog_save_file(
            "Select file ...",
            file_name=file_name,
            filter="*.bsp",
            allow_directory_change=False,
        )
        if rsp[0]:
            bspfile = rsp[2]  # file name without path
        else:
            return

    # Add waitbox
    wb = app.gui.window.dialog_wait("Performing nesting step 2 ...")

    # Get the folder name of the selected file
    path = os.path.dirname(overall_model_file)

    if overall_model_type == "sfincs_cht":
        overall_model = SFINCS()
        overall_model.path = path
    elif overall_model_type == "hurrywave":
        overall_model = HurryWave()
        overall_model.path = path

    obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix")

    okay = nest2(
        overall_model,
        app.active_model.domain,
        obs_point_prefix=obs_point_prefix,
        boundary_water_level_correction=0.0,
    )

    wb.close()

    if okay:
        print("Nesting step 2 completed successfully")
        # Update observations layer and save the observation points
        if app.active_model.name == "sfincs_cht":
            if overall_model_type == "hurrywave":
                app.active_model.domain.snapwave.boundary_conditions.write_boundary_conditions_timeseries()
            else:
                app.active_model.domain.input.variables.bzsfile = (
                    bzsfile  # file name without path
                )
                app.active_model.domain.boundary_conditions.write_boundary_conditions_timeseries()
        elif app.active_model.name == "hurrywave":
            app.active_model.domain.input.variables.bspfile = (
                bspfile  # file name without path
            )
            app.active_model.domain.boundary_conditions.write_boundary_conditions_spectra()


def _perform_nesting_step_2_hmt(overall_model_type: str, overall_model_file: str) -> None:
    """Nesting step 2 for the HydroMT-based models (sfincs_hmt, hurrywave_hmt).

    Reads the overall model output at the nesting observation points and sets
    (and writes) the boundary conditions of the active (detail) model:
    water levels for SFINCS in SFINCS, SnapWave time series for SFINCS in
    HurryWave, and spectra for HurryWave in HurryWave.
    """
    if not overall_model_file:
        app.gui.window.dialog_warning("Please load the overall model first.")
        return

    path = os.path.dirname(overall_model_file)
    detail = app.active_model.domain

    wb = app.gui.window.dialog_wait("Performing nesting step 2 ...")
    try:
        # Only the overall model's output folder is needed, not its full input
        if overall_model_type == "sfincs_hmt":
            from hydromt_sfincs import SfincsModel

            overall = SfincsModel(root=path, mode="r", write_gis=False)
        else:
            from hydromt_hurrywave import HurrywaveModel

            overall = HurrywaveModel(root=path, mode="r")

        obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix")
        correction = app.gui.getvar("nesting", "water_level_correction") or 0.0
        okay = nest2(
            overall,
            detail,
            obs_point_prefix=obs_point_prefix,
            output_path=path,
            boundary_water_level_correction=correction,
            # bc_path makes cht_nesting write the boundary conditions of the
            # detail model (to the detail model's own folder)
            bc_path=str(detail.root.path),
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        wb.close()
        app.gui.window.dialog_warning(f"Nesting step 2 failed:\n{e}")
        return
    wb.close()

    if okay is False:
        app.gui.window.dialog_warning(
            "Nesting step 2 is not available for this combination of models."
        )
        return
    print("Nesting step 2 completed successfully")
    app.gui.window.dialog_info(
        "Boundary conditions were generated and written. "
        "Save the model to update the input file.",
        "Nesting step 2",
    )