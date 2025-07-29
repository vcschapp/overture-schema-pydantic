from overture_schema_pydantic.scoping import Scope, scoped

import pytest

import re


def test_scope_field_name():
    for scope in Scope:
        field_name = scope._field_name
        assert isinstance(field_name, str)
        assert re.fullmatch(r"^[a-z_][a-z0-9_]*$", field_name)


def test_scoped_error_allowed_invalid_type_root():
    with pytest.raises(TypeError):
        scoped(123)


def test_scoped_error_allowed_invalid_member():
    with pytest.raises(TypeError):
        scoped([Scope.GEOMETRIC_POINT, "foo"])


def test_scoped_error_allowed_empty():
    with pytest.raises(ValueError):
        scoped([])


def test_scoped_error_required_not_in_allowed():
    with pytest.raises(ValueError):
        scoped([Scope.HEADING, Scope.SIDE], required=[Scope.GEOMETRIC_RANGE])
