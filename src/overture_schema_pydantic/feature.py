from overture_schema_pydantic.id import Id

from abc import ABC
from pydantic import BaseModel


class Feature(BaseModel, ABC):
    id: Id
