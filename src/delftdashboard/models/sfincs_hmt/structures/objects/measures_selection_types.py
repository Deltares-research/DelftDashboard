import os
from typing import Dict, List

from delftdashboard.app import app
from flood_adapt.object_model.interface.measures import IMeasure, MeasureModel
from geopandas import GeoDataFrame

from .measures_interfaces import ISelectionType


class PolygonSelectionType(ISelectionType):
    """Polygon selection type for measures. Parameters that need to be set for every measure type:
    - selection_type: polygon, import_area
    """

    def __init__(self):
        self._selection_type: str = "polygon"

    @property
    def selection_type(self) -> str:
        """Returns the selection type for the polygon measure type

        Returns
        -------
        str
            selection type

        Raises
        ------
        UnboundLocalError
            Selection type not set
        """
        if not self._selection_type:
            raise UnboundLocalError("Selection type not set")
        return self._selection_type

    @selection_type.setter
    def selection_type(self, value: str):
        """Sets the selection type for the polygon measure type

        Parameters
        ----------
        value : str
            selection type

        Raises
        ------
        ValueError
            Selection type not valid
        """
        if value not in self.get_measure_selection_types():
            raise ValueError("Selection type not valid")
        self._selection_type = value

    @staticmethod
    def get_measure_selection_types() -> List[str]:
        """Returns the possible measure selection types for the polygon measure category

        Returns
        -------
        list
            list of measure selection types
        """
        return ["polygon", "import_area"]

    @staticmethod
    def get_measure_selection_type_names() -> List[str]:
        """Returns the possible measure selection type names for the polygon measure category

        Returns
        -------
        list
            list of measure selection type names
        """
        return ["Draw polygon", "Import polygon"]

    def set_default_values(self):
        """Sets the default initialization values for the polygon measure type to the gui."""
        app.gui.setvar("measure", "geometry_file", "")

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the polygon measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """

        # Set editable values for measure type and selection type
        if self.selection_type == "polygon":
            app.gui.setvar("measure", "geometry_file", measure_attributes.polygon_file)
        elif self.selection_type == "import_area":
            # geometry_file is being set in the yml file
            pass

    def save_geojson_data(self, measure: Dict[str, str], measure_path: str) -> str:
        """Saves the geojson data for the polygon measure type

        Parameters
        ----------
        measure : dict
            measure data
        measure_path : str
            path to measure

        Returns
        -------
        str
            full path to geojson file
        """

        # Save geojson data if measure type is polygon 
        if self._selection_type == "polygon":
            gdf = app.gui.getvar("measures", "temp_gdf")
            gdf = GeoDataFrame(geometry=gdf["geometry"])
        elif self._selection_type == "import_area":
            path = app.gui.getvar("measure", "geometry_file")
            gdf = GeoDataFrame.from_file(path)
        else:
            # If the measure type is unknown, do nothing
            return

        path = os.path.join(measure_path, "measures", measure["name"])
        os.makedirs(path, exist_ok=True)
        file_name = os.path.join(path, measure["polygon_file"])

        with open(file_name, "w") as f:
            f.write(gdf.to_crs(4326).to_json(drop_id=True))

        return file_name

    def get_window_values(self) -> Dict[str, str]:
        """Returns the window values for the polygon measure type

        Returns
        -------
        dict
            dictionary of window values
        """

        if self.selection_type == "polygon" or self.selection_type == "import_area":
            return {
                "polygon_file": app.gui.getvar("measure", "name") + ".geojson",
                "selection_type": self.selection_type,
            }
        else:
            return {}

    @staticmethod
    def delete_window_values():
        """Deletes the window values for the polygon measure type"""
        app.gui.delvar("measure", "geometry_file")


class PolylineSelectionType(ISelectionType):
    """Polyline selection type for measures.
    Parameters that need to be set for every measure type:
    - selection_type: polyline, import_area
    - polygon_file: name of the geojson file
    """

    def __init__(self):
        self._selection_type: str = "polyline"

    @property
    def selection_type(self) -> str:
        """Returns the selection type for the polyline measure type

        Returns
        -------
        str
            selection type

        Raises
        ------
        UnboundLocalError
            Selection type not set
        """
        if not self._selection_type:
            raise UnboundLocalError("Selection type not set")
        return self._selection_type

    @selection_type.setter
    def selection_type(self, value: str):
        """Sets the selection type for the polyline measure type

        Parameters
        ----------
        value : str
            selection type

        Raises
        ------
        ValueError
            Selection type not valid
        """
        if value not in self.get_measure_selection_types():
            raise ValueError("Selection type not valid")
        self._selection_type = value

    @staticmethod
    def get_measure_selection_types() -> List[str]:
        """Returns the possible measure selection types for the polyline measure category

        Returns
        -------
        list
            list of measure selection types
        """
        return ["polyline", "import_area"]

    @staticmethod
    def get_measure_selection_type_names() -> List[str]:
        """Returns the possible measure selection type names for the polyline measure category

        Returns
        -------
        list
            list of measure selection type names
        """
        return ["Draw polyline", "Import polyline"]

    def set_default_values(self):
        """Sets the default initialization values for the polyline measure type to the gui"""
        # Nothing to be set
        pass

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the polyline measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """

        if self.selection_type == "polyline":
            app.gui.setvar("measure", "geometry_file", measure_attributes.polygon_file)
        elif self.selection_type == "import_area":
            # geometry_file is being set in the yml file
            pass

    def save_geojson_data(self, measure: Dict[str, str], measure_path: str) -> str:
        """Saves the geojson data for the polyline measure type

        Parameters
        ----------
        measure : dict
            measure data
        measure_path : str
            path to measure

        Returns
        -------
        str
            full path to geojson file
        """
        if self._selection_type == "polyline":
            gdf = app.gui.getvar("measures", "temp_gdf")
            gdf = GeoDataFrame(geometry=gdf["geometry"])
        elif self._selection_type == "import_area":
            path = app.gui.getvar("measure", "geometry_file")
            gdf = GeoDataFrame.from_file(path)
        else:
            return

        path = os.path.join(measure_path, "measures", measure["name"])
        os.makedirs(path, exist_ok=True)
        file_name = os.path.join(path, measure["polygon_file"])
        with open(file_name, "w") as f:
            f.write(gdf.to_crs(4326).to_json(drop_id=True))

        return file_name

    def get_window_values(self) -> Dict[str, str]:
        """Returns the window values for the polyline measure type

        Returns
        -------
        dict
            dictionary of window values
        """

        return_dict = {"polygon_file": app.gui.getvar("measure", "name") + ".geojson"}
        if self._selection_type == "polyline":
            return return_dict | {"selection_type": "polyline"}
        elif self._selection_type == "import_area":
            return return_dict | {"selection_type": "import_area"}

    @staticmethod
    def delete_window_values():
        """Deletes the window values for the polyline measure type"""
        app.gui.delvar("measure", "geometry_file")


class PointSelectionType(ISelectionType):
    """Point selection type for measures"""

    def __init__(self):
        self._selection_type: str = "point"

    @property
    def selection_type(self) -> str:
        """Returns the selection type for the polyline measure type

        Returns
        -------
        str
            selection type

        Raises
        ------
        UnboundLocalError
            Selection type not set
        """
        if not self._selection_type:
            raise UnboundLocalError("Selection type not set")
        return self._selection_type

    @selection_type.setter
    def selection_type(self, value: str):
        """Sets the selection type for the polyline measure type

        Parameters
        ----------
        value : str
            selection type

        Raises
        ------
        ValueError
            Selection type not valid
        """
        if value not in self.get_measure_selection_types():
            raise ValueError("Selection type not valid")
        self._selection_type = value

    @staticmethod
    def get_measure_selection_types() -> List[str]:
        """Returns the possible measure selection types for the point measure category

        Returns
        -------
        list
            list of measure selection types
        """
        return ["point", "import_area"]

    @staticmethod
    def get_measure_selection_type_names() -> List[str]:
        """Returns the possible measure selection type names for the point measure category

        Returns
        -------
        list
            list of measure selection type names
        """
        return ["Draw point", "Import point"]

    def set_default_values(self):
        """Sets the default initialization values for the point measure type to the gui"""
        # Nothing to be set
        pass

    def set_editable_values(self, measure_attributes: MeasureModel):
        """Sets the editable values for the point measure type

        Parameters
        ----------
        measure_attributes : MeasureModel
            measure attributes
        """
        # Nothing to be set
        pass

    def save_geojson_data(
        self, measure: Dict[str, str], measure_obj: IMeasure, gdf: GeoDataFrame
    ):
        """Saves the geojson data for the point measure type

        Parameters
        ----------
        measure : dict
            measure data
        measure_obj : IMeasure
            measure object
        gdf : GeoDataFrame
            geodataframe of measure
        """
        # Nothing to be saved
        pass

    def get_window_values(self):
        """Returns the window values for the point measure type

        Returns
        -------
        dict
            dictionary of window values
        """
        # Nothing to be returned
        return {}

    @staticmethod
    def delete_window_values():
        """Deletes the window values for the polyline measure type"""
        pass
