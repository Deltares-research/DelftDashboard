from abc import (
    ABC,
    abstractmethod,
    abstractproperty,
    abstractstaticmethod,
)
from typing import Dict, List, Union
import geopandas as gpd
from flood_adapt.object_model.interface.measures import IMeasure, MeasureModel
from hydromt_sfincs import SfincsModel


class ISelectionType(ABC):
    @abstractproperty
    def selection_type(self):
        ...

    @selection_type.setter
    def selection_type(self, value: str):
        ...

    @abstractstaticmethod
    def set_aggregation_area_list(*args):
        ...

    @abstractstaticmethod
    def get_measure_selection_types() -> List[str]:
        ...

    @abstractstaticmethod
    def get_measure_selection_type_names() -> List[str]:
        ...

    @abstractmethod
    def set_default_values(self):
        ...

    @abstractmethod
    def set_editable_values(self, measure_attributes: MeasureModel):
        ...

    @abstractmethod
    def save_geojson_data(self, measure: Dict[str, str], measure_obj: IMeasure):
        ...

    @abstractmethod
    def get_window_values(self) -> Dict[str, str]:
        ...

    @abstractstaticmethod
    def delete_window_values():
        ...


class IMeasureType(ABC):
    @abstractproperty
    def measure_type(self):
        ...

    @abstractproperty
    def selection_class(self):
        ...

    @selection_class.setter
    def selection_class(self, value: str):
        ...

    @abstractmethod
    def set_default_values(self):
        ...

    @abstractmethod
    def set_editable_values(self, measure_attributes: MeasureModel):
        ...

    @abstractmethod
    def get_window_values(self) -> Dict[str, Union[str, float, int, bool, dict]]:
        ...

    @abstractmethod
    def delete_window_values(self):
        ...

    @abstractmethod
    def add_to_model(
        self,
        measure_attributes: MeasureModel,
        sfincs_model: SfincsModel,
        gdf: gpd.GeoDataFrame,
    ):
        ...


class IMeasureTypeFactory(ABC):
    @abstractmethod
    def get_measure_type(self, measure_type: str) -> IMeasureType:
        ...

    @abstractmethod
    def get_measure_types(self) -> List[str]:
        ...

    @abstractmethod
    def get_measure_type_names(self) -> List[str]:
        ...


class IMeasureCategoryFactory(ABC):
    @abstractstaticmethod
    def get_measure_category_factory(measure_category: str) -> IMeasureTypeFactory:
        ...

    @abstractstaticmethod
    def get_measure_category_list() -> List[str]:
        ...

    @abstractstaticmethod
    def get_measure_category_names() -> List[str]:
        ...
