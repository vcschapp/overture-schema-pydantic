from overture_schema_pydantic.language import LanguageTag
from overture_schema_pydantic.constraint import MinItems, NoAdditionalProperties

from abc import ABC
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field, GetCoreSchemaHandler, BaseModel
from pydantic_core import core_schema


class Names(BaseModel):
    primary: str
    common: Optional[
        Annotated[Dict[LanguageTag, str], MinItems(1), NoAdditionalProperties()]
    ] = None
