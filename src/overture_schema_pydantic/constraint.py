from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import get_origin, Any

from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
    ValidationInfo,
)
from pydantic_core import core_schema, InitErrorDetails


class CollectionConstraint(ABC):
    @abstractmethod
    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        origin = get_origin(source)
        if not CollectionConstraint.__is_collection_type__(source):
            raise TypeError(
                f"{type(self).__name__} can only be applied to collections; but it was applied to {source.__name__}"
            )
        return handler(source)

    @staticmethod
    def __is_collection_type__(tp: type[Any]) -> bool:
        origin = get_origin(tp)
        if origin is not None:
            return issubclass(origin, Collection)
        else:
            return issubclass(tp, Collection)


class MinItems(CollectionConstraint):
    def __init__(self, min_items: int):
        if not isinstance(min_items, int):
            raise ValueError(
                f"`min_items` must be an `int` but it is a `{type(min_items).__name__}`"
            )
        elif min_items < 1:
            raise ValueError(f"`min_items` must be positive, but it is {min_items}")
        self.__min_items = min_items

    @property
    def min_items(self) -> int:
        return self.__min_items

    def validate(self, value: Any, info: ValidationInfo):
        num_items = len(value)
        if num_items < self.min_items:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"collection has too few items: expected len>={self.min_items} but got len={num_items})"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        schema = super().__get_pydantic_core_schema__(source, handler)
        return core_schema.with_info_after_validator_function(self.validate, schema)

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        print(f"GETTING JSON SCHEMA min_items={self.min_items}")

        json_schema = handler(core_schema)

        schema_type = json_schema.get("type")
        if schema_type == "array":
            json_schema["minItems"] = self.min_items
        elif schema_type == "object":
            json_schema["minProperties"] = self.min_items

        return json_schema
