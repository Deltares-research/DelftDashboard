from typing import Dict

from delftdashboard.app import app
from flood_adapt.object_model.interface.measures import (
    MeasureModel,
)

from .measures_interfaces import IMeasureType, ISelectionType
from hydromt_sfincs import SfincsModel
import geopandas as gpd


class BaseMeasureType(IMeasureType):
    """Parent for the general measure type, consisting of functions that are shared by all measure types. Parameters that are set in the gui:
    - name
    - description
    - selected_measure_type
    - selection type
    """

    def __init__(self):
        self._measure_type = None
        self._selection_class = None

    @property
    def measure_type(self) -> str:
        if not self._measure_type:
            raise UnboundLocalError("Measure type not set")
        return self._measure_type

    @property
    def selection_class(self) -> ISelectionType:
        if not self._selection_class:
            raise UnboundLocalError("Selection class not set")
        return self._selection_class

    @selection_class.setter
    def selection_class(self, value: str):
        raise NotImplementedError("Selection class cannot be set from the base class")

    def set_default_values(self):
        """Sets the default initialization values for the general measure type to the gui"""
        app.gui.setvar("measure", "name", "")
        app.gui.setvar("measure", "description", "")
        app.gui.setvar(
            "measure",
            "selected_measure_type",
            app.gui.getvar("measures", "selected_measure_type"),
        )
        app.gui.setvar(
            "measure",
            "selection_type",
            app.gui.getvar("measures", "selected_measure_selection_type"),
        )

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the general measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """
        app.gui.setvar("measure", "name", measure_attributes.name)
        app.gui.setvar("measure", "description", measure_attributes.description)
        app.gui.setvar("measure", "selected_measure_type", measure_attributes.type)
        app.gui.setvar(
            "measure", "selection_type", self._selection_class.selection_type
        )

    def get_window_values(self) -> Dict[str, str]:
        """Returns the window values for the measure type

        Returns
        -------
        dict
            window values
        """

        return {
            "name": app.gui.getvar("measure", "name"),
            "description": app.gui.getvar("measure", "description"),
            "type": self._measure_type,
            "selection_type": self._selection_class.selection_type,
        }

    def add_to_model(
        self,
        measure_attributes: MeasureModel,
        sfincs_model: SfincsModel,
        gdf: gpd.GeoDataFrame,
    ):
        """Adds the measure to the model

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        sfincs_model : SfincsModel
            sfincs model
        gdf : gpd.GeoDataFrame
            GeoDataFrame
        """
        raise NotImplementedError("Add to model not implemented for base measure type")

    def delete_window_values(self):
        """Deletes the window values for the measure type"""
        app.gui.delvar("measure", "name")
        app.gui.delvar("measure", "description")
        app.gui.delvar("measure", "selected_measure_type")
        app.gui.delvar("measure", "selection_type")
