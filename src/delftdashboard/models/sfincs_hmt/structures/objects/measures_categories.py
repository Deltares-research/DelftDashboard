from typing import List

from .measures_hydraulic import HydraulicMeasureFactory
from .measures_interfaces import IMeasureCategoryFactory, IMeasureTypeFactory


class MeasureCategoryFactory(IMeasureCategoryFactory):
    """Measure category factory for measures"""

    @staticmethod
    def get_measure_category_factory(measure_category: str) -> IMeasureTypeFactory:
        """Returns the measure category factory

        Parameters
        ----------
        measure_category : str
            measure category

        Returns
        -------
        IMeasureTypeFactory
            measure category factory

        Raises
        ------
        ValueError
            if measure category is not found in measure category factory
        """

        # TODO: For now, only hydrolic measures are supported, but this can be extended
        if measure_category == "hydraulic":
            return HydraulicMeasureFactory()
        else:
            raise ValueError(
                f"Measure category {measure_category} not found in measure category factory"
            )

    @staticmethod
    def get_measure_category_list() -> List[str]:
        """Returns the measure category list

        Returns
        -------
        list
            list of measure categories
        """

        return ["hydraulic"]

    @staticmethod
    def get_measure_category_names() -> List[str]:
        """Returns the measure category names

        Returns
        -------
        list
            list of measure category names
        """

        return ["Hydraulic"]
