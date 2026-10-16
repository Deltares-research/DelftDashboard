"""GUI callbacks for nesting step 1: add observation points from the overall model to the detail model."""

from __future__ import annotations

import os
from typing import Any

from cht_hurrywave import HurryWave
from cht_nesting import nest1
from cht_sfincs import SFINCS

from delftdashboard.app import app
from delftdashboard.operations import map


def select(*args: Any) -> None:
    """Activate the nest-1 tab and reset detail model state.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    map.update()
    # Set detail model loaded to False to avoid confusion
    app.gui.setvar("nesting", "detail_model_type", "")
    app.gui.setvar("nesting", "detail_model_loaded", False)
    update()


def update(*args: Any) -> None:
    """Refresh the list of available detail model types for the active model.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    # Set the detail model names
    if app.active_model.name == "sfincs_cht":
        detail_model_types = ["sfincs_cht"]
    elif app.active_model.name == "sfincs_hmt":
        detail_model_types = ["sfincs_hmt"]
    elif app.active_model.name == "delft3dfm":
        detail_model_types = ["sfincs_cht", "delft3dfm"]
    elif app.active_model.name == "hurrywave":
        detail_model_types = ["sfincs_cht", "hurrywave"]
    elif app.active_model.name == "hurrywave_hmt":
        detail_model_types = ["sfincs_hmt", "hurrywave_hmt"]
    else:
        detail_model_types = []

    # Drop any types that aren't actually loaded as models in this session.
    detail_model_types = [t for t in detail_model_types if t in app.model]
    app.gui.setvar("nesting", "detail_model_types", detail_model_types)

    # Check if the current model name is in the detail model names. If the
    # list is empty (no compatible detail model loaded) leave the var alone.
    detail_model_type = app.gui.getvar("nesting", "detail_model_type")
    if detail_model_types and detail_model_type not in detail_model_types:
        app.gui.setvar(
            "nesting",
            "detail_model_type",
            detail_model_types[0],
        )

    # Set the detail model long names
    long_names = [app.model[m].long_name for m in detail_model_types]
    app.gui.setvar("nesting", "detail_model_type_long_names", long_names)

    app.gui.window.update()


def load_detail_model(*args: Any) -> None:
    """Open a file dialog and load the detail model input file.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    detail_model_type = app.gui.getvar("nesting", "detail_model_type")

    if detail_model_type == "sfincs_cht":
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="sfincs.inp",
            filter="sfincs.inp",
            allow_directory_change=True,
        )
    elif detail_model_type in ("hurrywave", "hurrywave_hmt"):
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="hurrywave.inp",
            filter="hurrywave.inp",
            allow_directory_change=True,
        )
    elif detail_model_type == "sfincs_hmt":
        rsp = app.gui.window.dialog_open_file(
            "Select file ...",
            file_name="sfincs.inp",
            filter="sfincs.inp",
            allow_directory_change=True,
        )
    else:
        # This should never happen
        print("Unknown detail model name: ", detail_model_type)
        return

    if rsp[0]:
        app.gui.setvar("nesting", "detail_model_file", rsp[0])
        app.gui.setvar("nesting", "detail_model_loaded", True)
    else:
        app.gui.setvar("nesting", "detail_model_file", "")
        app.gui.setvar("nesting", "detail_model_loaded", False)
        return


def select_detail_model_type(*args: Any) -> None:
    """Reset the loaded state when the detail model type changes.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    app.gui.setvar("nesting", "detail_model_loaded", False)


def edit_obs_point_prefix(*args: Any) -> None:
    """Handle edits to the observation point prefix (no-op placeholder).

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    pass


def perform_nesting_step_1(*args: Any) -> None:
    """Execute nesting step 1: add observation points to the overall model at detail boundary locations.

    Parameters
    ----------
    *args : Any
        Unused GUI callback arguments.
    """
    detail_model_type = app.gui.getvar("nesting", "detail_model_type")
    detail_model_file = app.gui.getvar("nesting", "detail_model_file")

    if app.active_model.name in ("sfincs_hmt", "hurrywave_hmt"):
        _perform_nesting_step_1_hmt(detail_model_type, detail_model_file)
        return

    if app.active_model.name == "sfincs_cht":
        # Points were only added to the sfincs_cht model. Need to know new file name.
        file_name = app.model["sfincs_cht"].domain.input.variables.obsfile
        if not file_name:
            file_name = "sfincs.obs"
        rsp = app.gui.window.dialog_save_file(
            "Select file ...",
            file_name=file_name,
            filter="*.obs",
            allow_directory_change=False,
        )
        if rsp[0]:
            obsfile = rsp[2]  # file name without path
        else:
            return

    elif app.active_model.name == "hurrywave":
        if detail_model_type == "sfincs_cht":
            # Getting time series for SnapWave
            spectra = False
        else:
            # Getting spectra for other wave model
            spectra = True
        # Points were only added to the sfincs_cht model. Need to know new file name, but also it we need osp and obs files.
        if spectra:
            file_name = app.model["hurrywave"].domain.input.variables.ospfile
            if not file_name:
                file_name = "hurrywave.osp"
            rsp = app.gui.window.dialog_save_file(
                "Select file ...",
                file_name=file_name,
                filter="*.osp",
                allow_directory_change=False,
            )
            if rsp[0]:
                ospfile = rsp[2]  # file name without path
            else:
                return
        else:
            file_name = app.model["hurrywave"].domain.input.variables.obsfile
            if not file_name:
                file_name = "hurrywave.obs"
            rsp = app.gui.window.dialog_save_file(
                "Select file ...",
                file_name=file_name,
                filter="*.obs",
                allow_directory_change=False,
            )
            if rsp[0]:
                obsfile = rsp[2]  # file name without path
            else:
                return

    # Add waitbox
    wb = app.gui.window.dialog_wait("Performing nesting step 1 ...")

    # Get the folder name of the selected file
    path = os.path.dirname(detail_model_file)

    print("Reading detail model ...")
    if detail_model_type == "sfincs_cht":
        detail_model = SFINCS()
        detail_model.path = path
        detail_model.read()
    elif detail_model_type == "hurrywave":
        detail_model = HurryWave()
        detail_model.path = path
        detail_model.read()

    # Do some checks here
    if detail_model_type == "sfincs_cht" and app.active_model.name == "hurrywave":
        # Make sure that SnapWave is activated in the sfincs_cht model
        if not detail_model.input.variables.snapwave:
            wb.close()
            app.gui.window.dialog_warning(
                "SnapWave is not activated in the SFINCS model. It can not be nested in HurryWave."
            )
            return
        # Make sure that there is a bwv file in the sfincs_cht model
        if not detail_model.input.variables.snapwave_bndfile:
            wb.close()
            app.gui.window.dialog_warning(
                "No snapwave bnd file found in the SFINCS model. It can not be nested in HurryWave."
            )
            return

    obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix")

    okay = nest1(
        app.active_model.domain, detail_model, obs_point_prefix=obs_point_prefix
    )

    wb.close()

    if okay:
        print("Nesting step 1 completed successfully")
        # Update observations layer and save the observation points
        if app.active_model.name == "sfincs_cht":
            app.active_model.domain.input.variables.obsfile = (
                obsfile  # file name without path
            )
            app.active_model.domain.observation_points.write()
            gdf = app.active_model.domain.observation_points.gdf
            app.map.layer["sfincs_cht"].layer["observation_points"].set_data(gdf, 0)
            app.gui.setvar("sfincs_cht", "active_observation_point", 0)
            app.gui.setvar("sfincs_cht", "nr_observation_points", len(gdf))
        elif app.active_model.name == "hurrywave":
            if spectra:
                app.active_model.domain.input.variables.ospfile = (
                    ospfile  # file name without path
                )
                app.active_model.domain.observation_points_sp2.write()
                gdf = app.active_model.domain.observation_points_sp2.gdf
                app.map.layer["hurrywave"].layer["observation_points_spectra"].set_data(
                    gdf, 0
                )
                app.gui.setvar("hurrywave", "active_observation_point_spectra", 0)
                app.gui.setvar("hurrywave", "nr_observation_points_spectra", len(gdf))
            else:
                app.active_model.domain.input.variables.obsfile = (
                    obsfile  # file name without path
                )
                app.active_model.domain.observation_points_regular.write()
                gdf = app.active_model.domain.observation_points_regular.gdf
                app.map.layer["hurrywave"].layer["observation_points_regular"].set_data(
                    gdf, 0
                )
                app.gui.setvar("hurrywave", "active_observation_point_regular", 0)
                app.gui.setvar("hurrywave", "nr_observation_points_regular", len(gdf))


def _read_hmt_model(model_type: str, path: str) -> Any:
    """Read a hydromt_sfincs / hydromt_hurrywave model (read-only)."""
    if model_type == "sfincs_hmt":
        from hydromt_sfincs import SfincsModel

        model = SfincsModel(root=path, mode="r", write_gis=False)
    else:
        from hydromt_hurrywave import HurrywaveModel

        model = HurrywaveModel(root=path, mode="r")
    model.read()
    return model


def _perform_nesting_step_1_hmt(detail_model_type: str, detail_model_file: str) -> None:
    """Nesting step 1 for the HydroMT-based models (sfincs_hmt, hurrywave_hmt).

    Adds observation points to the active (overall) model at the boundary
    points of the detail model and writes them to the observation file.
    """
    overall_name = app.active_model.name
    overall = app.active_model.domain

    if not detail_model_file:
        app.gui.window.dialog_warning("Please load a detail model first.")
        return

    # Which observation point component / file / map layer receives the points
    if overall_name == "hurrywave_hmt" and detail_model_type == "hurrywave_hmt":
        # Spectra for the detail HurryWave model
        component, file_key, default_file = (
            "observation_points_spectra", "ospfile", "hurrywave.osp")
        layer, active_var, nr_var = (
            "observation_points_spectra",
            "active_observation_point_spectra",
            "nr_observation_points_spectra",
        )
        filt = "*.osp"
    else:
        # Time series (SFINCS in SFINCS, or SnapWave in HurryWave)
        component, file_key = "observation_points", "obsfile"
        default_file = "sfincs.obs" if overall_name == "sfincs_hmt" else "hurrywave.obs"
        if overall_name == "sfincs_hmt":
            layer, active_var, nr_var = (
                "observation_points", "active_observation_point",
                "nr_observation_points")
        else:
            layer, active_var, nr_var = (
                "observation_points_regular", "active_observation_point_regular",
                "nr_observation_points_regular")
        filt = "*.obs"

    file_name = overall.config.get(file_key) or default_file
    rsp = app.gui.window.dialog_save_file(
        "Select file ...",
        file_name=os.path.basename(str(file_name)),
        filter=filt,
        allow_directory_change=False,
    )
    if not rsp[0]:
        return
    obs_file = rsp[2]  # file name without path

    wb = app.gui.window.dialog_wait("Performing nesting step 1 ...")
    try:
        path = os.path.dirname(detail_model_file)
        print("Reading detail model ...")
        detail = _read_hmt_model(detail_model_type, path)

        # SFINCS nested in HurryWave: needs SnapWave boundary points
        if detail_model_type == "sfincs_hmt" and overall_name == "hurrywave_hmt":
            if len(detail.snapwave_boundary_conditions.gdf) == 0:
                wb.close()
                app.gui.window.dialog_warning(
                    "The SFINCS model has no SnapWave boundary points. It can "
                    "not be nested in HurryWave."
                )
                return
        elif detail_model_type == "sfincs_hmt":
            if len(detail.water_level.gdf) == 0:
                wb.close()
                app.gui.window.dialog_warning(
                    "The detail SFINCS model has no water level boundary points."
                )
                return
        elif len(detail.boundary_conditions.gdf) == 0:
            wb.close()
            app.gui.window.dialog_warning(
                "The detail HurryWave model has no boundary points."
            )
            return

        obs_point_prefix = app.gui.getvar("nesting", "obs_point_prefix")
        okay = nest1(overall, detail, obs_point_prefix=obs_point_prefix)
    except Exception as e:
        import traceback

        traceback.print_exc()
        wb.close()
        app.gui.window.dialog_warning(f"Nesting step 1 failed:\n{e}")
        return
    wb.close()

    if not okay:
        app.gui.window.dialog_warning(
            "Nesting step 1 is not available for this combination of models."
        )
        return

    print("Nesting step 1 completed successfully")
    overall.config.set(file_key, obs_file)
    getattr(overall, component).write()
    gdf = getattr(overall, component).gdf
    app.map.layer[overall_name].layer[layer].set_data(gdf, 0)
    app.gui.setvar(overall_name, active_var, 0)
    app.gui.setvar(overall_name, nr_var, len(gdf))
    app.gui.window.update()