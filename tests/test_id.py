from overture_schema_pydantic.id import Id

import pytest
from pydantic import BaseModel, ValidationError


class DummyModel(BaseModel):
    id: Id


def test_valid():
    m = DummyModel(id="foo")
    assert m.id == "foo"


def test_empty():
    with pytest.raises(ValidationError):
        DummyModel(id="")


def test_blank():
    with pytest.raises(ValidationError):
        DummyModel(id=" ")


def test_whitespace():
    with pytest.raises(ValidationError):
        DummyModel(id=" foo ")
