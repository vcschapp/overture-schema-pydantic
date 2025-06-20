from overture_schema_pydantic.feature import Feature

import copy
from typing import Any

import pytest
from pydantic import ValidationError


class DummyFeature(Feature):
    pass


VALID_STARTING_POINT = {
    'id': 'foo',
    'type': 'bar',
    'geometry': { 'type': 'Point', 'coordinates': [0, 0]}
}

def test_valid():
    m = DummyFeature(**VALID_STARTING_POINT)

    assert m.id == "foo"
    assert m.type == 'bar'
    assert m.geometry.geom.geom_type == 'Point'

def delete_key(d: dict, k: Any) -> None:
    del d[k]
    return None

def set_key(d: dict, k: Any, v: Any) -> None:
    d[k] = v
    return None

@pytest.mark.parametrize("name,permute", [
    ('id_missing', lambda d: delete_key(d, 'id')),
    ('id_empty', lambda d: set_key(d, 'id', '')),
    ('id_blank', lambda d: set_key(d, 'id', ' ')),
    ('id_whitespace', lambda d: set_key(d, 'id', ' foo ')),
    ('type_missing', lambda d: delete_key(d, 'type')),
    ('type_empty', lambda d: set_key(d, 'type', '')),
    ('type_blank', lambda d: set_key(d, 'type', ' ')),
    ('type_whitespace', lambda d: set_key(d, 'type', ' foo ')),
    ('geometry_missing', lambda d: delete_key(d, 'geometry')),
    ('geometry_string', lambda d: set_key(d, 'geometry', 'foo')),
    ('geometry_type_missing', lambda d: delete_key(d['geometry'], 'type')),
    ('geometry_type_invalid', lambda d: set_key(d['geometry'], 'type', 'Triangle')),
    ('geometry_coordinates_missing', lambda d: delete_key(d['geometry'], 'coordinates')),
])
def test_invalid(name, permute):
    d = copy.deepcopy(VALID_STARTING_POINT)
    permute(d)
    with pytest.raises(ValidationError):
        DummyFeature(**d)
