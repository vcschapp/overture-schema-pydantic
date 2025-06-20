from overture_schema_pydantic.id import Id

from abc import ABC
from enum import Enum
from typing import Any

from pydantic import GetCoreSchemaHandler, BaseModel
from pydantic_core import core_schema


class FeatureType(str, Enum):
    ADDRESS = "address"
    BATHYMETRY = "bathymetry"
    BUILDING = "building"
    BUILDING_PART = "building_part"
    CONNECTOR = "connector"
    DIVISION = "division"
    DIVISION_AREA = "division_area"
    DIVISION_BOUNDARY = "division_boundary"
    INFRASTRUCTURE = "infrastructure"
    LAND = "land"
    LAND_COVER = "land_cover"
    LAND_USE = "land_use"
    PLACE = "place"
    SEGMENT = "segment"
    WATER = "water"


class FeatureTypeReference:
    def __init__(self, feature_type: FeatureType):
        self.__feature_type = FeatureType(feature_type)

    @property
    def feature_type(self) -> FeatureType:
        self.__feature_type

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, Id):
            raise TypeError(
                f"{FeatureTypeReference.__name__} can only be applied to {Id.__name__}; but it was applied to {source.__name__}"
            )
        schema = handler(source)
        return schema


class Feature(BaseModel, ABC):
    id: Id
