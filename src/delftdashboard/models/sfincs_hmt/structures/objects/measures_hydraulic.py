from typing import Dict, List, Union

from flood_adapt.object_model.interface.measures import (
    MeasureModel,
)

from delftdashboard.app import app

from hydromt_sfincs import SfincsModel

from .measures_general import BaseMeasureType
from .measures_interfaces import IMeasureType, IMeasureTypeFactory
from .measures_selection_types import (
    PolylineSelectionType,
)

import geopandas as gpd


class HydraulicMeasureFactory(IMeasureTypeFactory):
    """Hydraulic measure factory for measures part of hydraulic infrastructure"""

    @staticmethod
    def get_measure_type(measure_type: str) -> IMeasureType:
        """Returns the measure type for the hydraulic measure factory

        Parameters
        ----------
        measure_type : str
            measure type

        Returns
        -------
        IMeasureType
            measure type

        Raises
        ------
        ValueError
            if measure type is not found in hydraulic measure factory
        """

        if measure_type == "floodwall":
            return Floodwall()
        elif measure_type == "pump":
            return Pump()
        elif measure_type == "culvert":
            return Culvert()
        elif measure_type == "thin_dam":
            return ThinDam()
        else:
            raise ValueError(
                f"Measure type {measure_type} not found in hydraulic measure factory"
            )

    def get_measure_types(self) -> List[str]:
        """Returns the possible measure types for the hydraulic measure category

        Returns
        -------
        list
            list of measure types
        """
        return ["floodwall", "pump", "culvert", "thin_dam"]

    def get_measure_type_names(self) -> List[str]:
        """Returns the possible measure type names for the hydraulic measure category

        Returns
        -------
        list
            list of measure type names
        """
        return ["Floodwall", "Pump", "Culvert", "Thin dam"]


class Floodwall(BaseMeasureType):
    """Floodwall measure type for measures at hydraulic level. Parameters that are set in the gui:
    - elevation
    - elevation text
    """

    def __init__(self):
        super().__init__()
        self._measure_type = "floodwall"
        self._selection_class = PolylineSelectionType()

    @BaseMeasureType.selection_class.setter
    def selection_class(self, value: str):
        """Sets the selection class for the floodwall measure type

        Parameters
        ----------
        value : str
            selection class
        """
        self._selection_class.selection_type = value

    def set_default_values(self):
        """Sets the default initialization values for the floodwall measure type to the gui"""

        # Set default values for measure type and selection type
        super().set_default_values()
        self._selection_class.set_default_values()

        # Set default values for floodwall measure type
        app.gui.setvar("measure", "elevation", 0.0)

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the floodwall measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """

        # Set editable values for measure type and selection type
        super().set_editable_values(measure_attributes)
        self._selection_class.set_editable_values(measure_attributes)

        # Set editable values for floodwall measure type
        app.gui.setvar("measure", "elevation", measure_attributes.elevation.value)

    def get_window_values(self) -> Dict[str, Union[str, dict]]:
        """Returns the window values for the floodwall measure type

        Returns
        -------
        dict
            dictionary of window values
        """

        # Return window values for floodwall
        return_values = {
            "elevation": {
                "value": app.gui.getvar("measure", "elevation"),
                "units": "meters",
            }
        }

        # Combine window values for floodwall with window values for measure type and selection type
        return (
            return_values
            | super().get_window_values()
            | self._selection_class.get_window_values()
        )

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
            geodataframe with floodwall geometry
        """

        # Add floodwall attributes to geodataframe
        gdf["name"] = measure_attributes.attrs.name
        gdf["z"] = measure_attributes.attrs.elevation.value
        gdf["par1"] = 0.6

        # HydroMT function: create floodwall
        sfincs_model.setup_structures(structures=gdf, stype="weir", merge=True)

    def delete_window_values(self):
        """Deletes the window values for the floodwall measure type"""

        # Delete window values for floodwall
        super().delete_window_values()
        self._selection_class.delete_window_values()

        # Delete window values for floodwall measure type
        app.gui.delvar("measure", "elevation")


class Drainage(BaseMeasureType):
    """Pump measure type for measures at hydraulic level. Parameters that are set in the gui:
    - discharge
    - discharge text
    """

    def __init__(self):
        super().__init__()
        self._measure_type = "drainage"
        self._selection_class = PolylineSelectionType()

    @BaseMeasureType.selection_class.setter
    def selection_class(self, value: str):
        """Sets the selection class for the pump measure type

        Parameters
        ----------
        value : str
            selection class
        """
        self._selection_class.selection_type = value

    def set_default_values(self):
        """Sets the default initialization values for the floodwall measure type to the gui"""

        # Set default values for measure type and selection type
        super().set_default_values()
        self._selection_class.set_default_values()

        # Set default values for pump measure type
        app.gui.setvar("measure", "discharge", 0.0)

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the floodwall measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """

        # Set editable values for measure type and selection type
        super().set_editable_values(measure_attributes)
        self._selection_class.set_editable_values(measure_attributes)

        # Set editable values for pump measure type
        app.gui.setvar("measure", "discharge", measure_attributes.discharge.value)

    def get_window_values(self) -> Dict[str, Union[str, dict]]:
        """Returns the window values for the pump measure type

        Returns
        -------
        dict
            dictionary of window values
        """

        # Return window values for pump
        return_values = {
            "discharge": {
                "value": app.gui.getvar("measure", "discharge"),
                "units": "m3/s",
            }
        }

        # Combine window values for pump with window values for measure type and selection type
        return (
            return_values
            | super().get_window_values()
            | self._selection_class.get_window_values()
        )

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
            geodataframe with pump geometry
        """

        # Add pump attributes to geodataframe
        gdf["name"] = measure_attributes.attrs.name

        # HydroMT function: create floodwall
        sfincs_model.setup_drainage_structures(
            structures=gdf,
            stype="pump",
            discharge=measure_attributes.attrs.discharge.value,
            merge=True,
        )

    def delete_window_values(self):
        """Deletes the window values for the pump measure type"""

        # Delete window values for pump
        super().delete_window_values()
        self._selection_class.delete_window_values()

        # Delete window values for pump measure type
        app.gui.delvar("measure", "discharge")


class Pump(Drainage):
    """Pump measure type for measures at hydraulic level. Parameters that are set in the gui:
    - discharge
    - discharge text
    """

    def __init__(self):
        super().__init__()
        self._measure_type = "pump"


class Culvert(Drainage):
    """Culvert measure type for measures at hydraulic level. Parameters that are set in the gui:
    - discharge
    - discharge text
    """

    def __init__(self):
        super().__init__()
        self._measure_type = "culvert"


class ThinDam(Floodwall):
    """ThinDam measure type for measures at hydraulic level. Parameters that are set in the gui:
    - elevation
    - elevation text
    A thin dam is a special kind of floodwall, with an infinite elevation (set to 1km in the database).
    """

    def __init__(self):
        super().__init__()
        self._measure_type = "thin_dam"
        self._selection_class = PolylineSelectionType()

    def set_default_values(self):
        """Sets the default initialization values for the floodwall measure type to the gui"""

        # Set default values for measure type and selection type
        super().set_default_values()

        # Overwrite the elevation to a very high value
        app.gui.setvar("measure", "elevation", 1000.0)

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
            geodataframe with floodwall geometry
        """

        # Add floodwall attributes to geodataframe
        gdf["name"] = measure_attributes.attrs.name
        gdf["z"] = measure_attributes.attrs.elevation.value
        gdf["par1"] = 0.6

        # HydroMT function: create floodwall
        sfincs_model.setup_structures(structures=gdf, stype="thd", merge=True)
