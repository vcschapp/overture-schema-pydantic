from overture_schema_pydantic.geometry import Geometry
from overture_schema_pydantic.id import Id

from abc import ABC
from enum import Enum
from typing import Annotated, Any

from pydantic import Field, GetCoreSchemaHandler, BaseModel
from pydantic_core import core_schema


"""
The category or type of a feature.

NOTE: I started having this be a string enum, but if we want the core
      Overture schema model package to support arbitrary extension to
      new feature types, I think we want to introduce the concept of
      Overture feature types at this level.
"""
FeatureType = Annotated[
    str,
    Field(
        min_length=1,
        max_length=32,
        pattern=r"^^[a-z][a-z0-9_]*$",
        description="The category or type of feature",
    ),
]


class FeatureTypeReference:
    def __init__(self, feature_type: FeatureType):
        self.__feature_type = feature_type # TODO: Validate this

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
    type: FeatureType
    geometry: Geometry
