from overture_schema_pydantic.feature import Feature

import pytest
from pydantic import ValidationError

class DummyFeature(Feature):
    pass

def test_valid():
    m = DummyFeature(id="foo")
    assert m.id == "foo"

def test_id_empty():
    with pytest.raises(ValidationError):
        DummyFeature(id="")

def test_id_blank():
    with pytest.raises(ValidationError):
        DummyFeature(id=" ")


def test_id_whitespace():
    with pytest.raises(ValidationError):
        DummyFeature(id=" foo ")
