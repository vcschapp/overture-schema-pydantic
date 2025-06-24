from overture_schema_pydantic.geometry import Geometry
from overture_schema_pydantic.id import Id
from overture_schema_pydantic.names import Names
from overture_schema_pydantic.source import Source

from abc import ABC
from typing import Annotated, Any, List, Optional

from pydantic import BaseModel, Field, GetCoreSchemaHandler, GetJsonSchemaHandler
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
        pattern=r"^[a-z][a-z0-9_]*$",
        description="The category or type of feature",
    ),
]


class FeatureTypeReference:
    def __init__(self, feature_type: FeatureType):
        self.__feature_type = feature_type  # TODO: Validate this

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
    geometry: Geometry
    type: FeatureType
    # TODO: should we scrap `theme` or keep it?
    # TODO: version
    # TODO: implement UniqueItems constraint annotation
    sources: Annotated[List[Source], Field(min_length=1)]
    names: Optional[Names] = None

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        # Modify the JSON Schema to validate as a GeoJSON feature.
        json_schema = handler(core_schema)

        # Move all non-GeoJSON properties down into the GeoJSON `properties` object.
        json_schema_top_level_required = json_schema.get("required", {})
        json_schema_top_level_properties = json_schema["properties"]
        geo_json_properties = {}
        geo_json_required = []
        for name in list(json_schema_top_level_properties.keys()):
            if name not in ["id", "geometry"]:
                value = json_schema_top_level_properties[name]
                geo_json_properties[name] = value
                del json_schema_top_level_properties[name]
                if name in json_schema_top_level_required:
                    json_schema_top_level_required.remove(name)
                    geo_json_required.append(name)
        geo_json_properties_schema = {
            "type": "object",
            "properties": geo_json_properties,
            "required": geo_json_required,
        }
        json_schema_top_level_properties["properties"] = {
            k: v for k, v in geo_json_properties_schema.items() if v
        }
        json_schema_top_level_required.append("properties")

        # Add the `"type": "Feature"` GeoJSON property at the top level.
        json_schema_top_level_properties["type"] = {
            "type": "string",
            "const": "Feature",
        }
        json_schema_top_level_required.append("type")

        # TODO: Special handling for bbox.

        # Done modifying to GeoJSON.
        return json_schema
