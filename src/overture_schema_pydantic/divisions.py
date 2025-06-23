from overture_schema_pydantic.feature import Feature
from overture_schema_pydantic.geometry import Geometry, GeometryTypeConstraint

from typing import Annotated, Literal


class Division(Feature):
    geometry: Annotated[Geometry, GeometryTypeConstraint("Point")]
    type: Literal["division"]
