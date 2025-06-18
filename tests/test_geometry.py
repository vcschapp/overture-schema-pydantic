from overture_schema_pydantic.geometry import Geometry, GeometryTypeConstraint

from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError

def test_empty_geometry_type_constraint():
    with pytest.raises(ValueError):
        class EmptyGeometryTypeConstraintModel(BaseModel):
            geometry: Annotated[Geometry, GeometryTypeConstraint()]


# class PointModel:
#     geometry: Geometry = Field(..., geometry_type = ('Point'))
