import datetime
import sys
from typing import get_args, get_origin, Annotated, Dict, List, Literal, Tuple, Union

from overture_schema_pydantic.geometry import Geometry

from pydantic import BaseModel

import libcst as cst
import black


def generate_code(model: type[BaseModel]) -> str:
    expr = pydantic_model_to_spark_type(model)
    module = cst.Module(body=[cst.SimpleStatementLine([cst.Expr(expr)])])
    raw_code = module.code
    pretty_code = black.format_str(raw_code, mode=black.Mode())
    return pretty_code


def pydantic_model_to_spark_type(model: type[BaseModel]) -> cst.BaseExpression:
    struct_fields = []
    for field_name, field_value in model.model_fields.items():
        struct_field_type_expr = python_type_to_spark_type(field_value.annotation)
        struct_field_name = field_name
        if field_value.alias is not None:
            struct_field_name = field_value.alias
        nullable = (
            cst.Name("True") if not field_value.is_required() else cst.Name("False")
        )
        struct_fields.append(
            cst.Element(
                cst.Call(
                    func=cst.Name("StructField"),
                    args=[
                        cst.Arg(cst.SimpleString(repr(struct_field_name))),
                        cst.Arg(struct_field_type_expr),
                        cst.Arg(nullable),
                    ],
                )
            )
        )
    return cst.Call(
        func=cst.Name("StructType"), args=[cst.Arg(cst.List(elements=struct_fields))]
    )


def python_type_to_spark_type(py_type: type) -> cst.BaseExpression:
    origin = get_origin(py_type)
    args = get_args(py_type)

    if origin is Annotated and len(args) >= 1:
        return python_type_to_spark_type(args[0])

    if origin is Union and type(None) in args:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return python_type_to_spark_type(non_none[0])
        raise TypeError(f"Unsupported Union: {py_type}")

    if origin in (list, List, tuple, Tuple):
        # TODO: Would be nice to support sets here also.
        inner_expr = python_type_to_spark_type(args[0])
        return cst.Call(func=cst.Name("ArrayType"), args=[cst.Arg(inner_expr)])

    if origin in (dict, Dict):
        k, v = args
        if not issubclass(k, str):
            raise TypeError(
                f"Spark MapType only supports string keys, but the key type for `{repr(py_type)}` is {repr(k)}"
            )
        return cst.Call(
            func=cst.Name("MapType"),
            args=[
                cst.Arg(cst.Call(func=cst.Name("StringType"), args=[])),
                cst.Arg(python_type_to_spark_type(v)),
            ],
        )

    if origin is Literal:
        # TODO: To handle enums we probably need to figure out the base type of the enum.
        return python_type_to_spark_type(type(args[0]))

    if isinstance(py_type, type) and issubclass(py_type, BaseModel):
        return pydantic_model_to_spark_type(py_type)

    if py_type is Geometry:
        return cst.Call(func=cst.Name("BinaryType"), args=[])

    primitive_mapping = {
        str: "StringType",
        # TODO: We would want to support ByteType, ShortType, IntegerType, FloatType, and DecimalType
        #       depending on the constraints applied to the field.
        int: "LongType",
        float: "DoubleType",
        bool: "BooleanType",
        # TODO: We might want to use string for timestamps.
        datetime.date: "DateType",
        datetime.datetime: "TimestampType",
    }

    if py_type in primitive_mapping:
        return cst.Call(func=cst.Name(primitive_mapping[py_type]), args=[])

    # TODO: This is dying on the `Annotated` values.
    raise TypeError(f"Unsupported type: {py_type}, origin={origin}")
