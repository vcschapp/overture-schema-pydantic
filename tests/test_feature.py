from overture_schema_pydantic.feature import Feature

import copy
from datetime import datetime, timezone, timedelta
from typing import Any

import pytest
from pydantic import ValidationError


class DummyFeature(Feature):
    pass


VALID_STARTING_POINT = {
    "id": "foo",
    "type": "bar",
    "geometry": {"type": "Point", "coordinates": [0, 0]},
    "sources": (
        {
            "property": "",
            "dataset": "foo",
        },
        {
            "property": "bar",
            "dataset": "baz",
            "record_id": "qux",
            "update_time": "2025-06-20T16:44:01-08:00",
            "confidence": 1,
        },
    ),
    "names": {
        "primary": "foo",
    },
}


def test_valid():
    m = DummyFeature(**VALID_STARTING_POINT)

    assert m.id == "foo"
    assert m.type == "bar"
    assert m.geometry.geom.geom_type == "Point"
    assert len(m.sources) == 2
    assert m.sources[0].property == ""
    assert m.sources[0].dataset == "foo"
    assert m.sources[0].record_id is None
    assert m.sources[0].update_time is None
    assert m.sources[0].confidence is None
    assert m.sources[1].property == "bar"
    assert m.sources[1].dataset == "baz"
    assert m.sources[1].record_id == "qux"
    assert m.sources[1].update_time == datetime(
        2025, 6, 20, 16, 44, 1, tzinfo=timezone(timedelta(hours=-8))
    )
    assert m.sources[1].confidence == 1
    assert m.names.primary == "foo"


def test_valid_remove_optional():
    optional = ["names"]

    d = copy.deepcopy(VALID_STARTING_POINT)
    for o in optional:
        del d[o]

    m = DummyFeature(**d)

    assert m.id == "foo"
    assert m.type == "bar"
    assert m.geometry.geom.geom_type == "Point"


def delete_key(d: dict, k: Any) -> None:
    del d[k]
    return None


def set_key(d: dict, k: Any, v: Any) -> None:
    d[k] = v
    return None


@pytest.mark.parametrize(
    "name,permute",
    [
        ("id_missing", lambda d: delete_key(d, "id")),
        ("id_empty", lambda d: set_key(d, "id", "")),
        ("id_blank", lambda d: set_key(d, "id", " ")),
        ("id_whitespace", lambda d: set_key(d, "id", " foo ")),
        ("type_missing", lambda d: delete_key(d, "type")),
        ("type_empty", lambda d: set_key(d, "type", "")),
        ("type_blank", lambda d: set_key(d, "type", " ")),
        ("type_whitespace", lambda d: set_key(d, "type", " foo ")),
        ("geometry_missing", lambda d: delete_key(d, "geometry")),
        ("geometry_string", lambda d: set_key(d, "geometry", "foo")),
        ("geometry_type_missing", lambda d: delete_key(d["geometry"], "type")),
        ("geometry_type_invalid", lambda d: set_key(d["geometry"], "type", "Triangle")),
        (
            "geometry_coordinates_missing",
            lambda d: delete_key(d["geometry"], "coordinates"),
        ),
        ("sources_missing", lambda d: delete_key(d, "sources")),
        ("sources_empty", lambda d: set_key(d, "sources", ())),
        ("sources_item_type_invalid", lambda d: set_key(d, "sources", ("foo", "bar"))),
        (
            "sources_item_property_missing",
            lambda d: set_key(d, "sources", ({"dataset": "foo"},)),
        ),
        (
            "sources_item_dataset_missing",
            lambda d: set_key(d, "sources", ({"property": "foo"},)),
        ),
        ("names_primary_missing", lambda d: delete_key(d["names"], "primary")),
        ("names_common_empty", lambda d: set_key(d["names"], "common", {})),
        (
            "names_common_invalid_language_tag",
            lambda d: set_key(d["names"], "common", {"!foo": "bar"}),
        ),
    ],
)
def test_invalid(name, permute):
    d = copy.deepcopy(VALID_STARTING_POINT)
    permute(d)
    with pytest.raises(ValidationError):
        DummyFeature(**d)
