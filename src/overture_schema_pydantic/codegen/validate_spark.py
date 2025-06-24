from typing import Optional
import re

from pydantic import BaseModel
from pydantic.fields import FieldInfo

import black
import libcst as cst


def generate_code(model: type[BaseModel]) -> str:
    module = generate_validation_module(model)
    raw_code = module.code
    pretty_code = black.format_str(raw_code, mode=black.Mode())
    return pretty_code


def generate_validation_module(
    model: type[BaseModel], main_function_name: Optional[str] = None
) -> cst.Module:
    model_name = model.__name__
    if main_function_name is None:
        main_function_name = f"validate_{to_snake_case(model_name)}"
    validation_errors_function_name = "validation_errors"

    imports = [
        cst.SimpleStatementLine(
            [
                cst.ImportFrom(
                    module=cst.Attribute(cst.Name("pyspark"), cst.Name("sql")),
                    names=[
                        cst.ImportAlias(cst.Name("DataFrame")),
                        cst.ImportAlias(cst.Name("Column")),
                    ],
                )
            ]
        ),
        cst.SimpleStatementLine(
            [
                cst.ImportFrom(
                    module=cst.Attribute(
                        cst.Attribute(cst.Name("pyspark"), cst.Name("sql")),
                        cst.Name("functions"),
                    ),
                    names=[
                        cst.ImportAlias(cst.Name("array")),
                        cst.ImportAlias(cst.Name("col")),
                        cst.ImportAlias(cst.Name("flatten")),
                        cst.ImportAlias(cst.Name("lit")),
                        cst.ImportAlias(cst.Name("size")),
                        cst.ImportAlias(cst.Name("struct")),
                        cst.ImportAlias(cst.Name("when")),
                    ],
                )
            ]
        ),
    ]

    columns = [
        (field_info.alias or field_name, field_info)
        for field_name, field_info in model.model_fields.items()
    ]

    main_func = generate_validation_main_function(
        model, main_function_name, validation_errors_function_name
    )
    errors_func = generate_validation_errors_function(
        model, validation_errors_function_name, [column[0] for column in columns]
    )

    funcs = [
        main_func,
        errors_func,
        *(
            generate_validation_column_function(
                validation_errors_function_name, column[0], column[1]
            )
            for column in columns
        ),
    ]

    return cst.Module(body=imports + funcs)


def generate_validation_main_function(
    model: type[BaseModel],
    main_function_name: str,
    validation_errors_function_name: str,
) -> cst.FunctionDef:
    with_column_call = cst.Call(
        func=cst.Attribute(value=cst.Name("df"), attr=cst.Name("withColumn")),
        args=[
            cst.Arg(cst.SimpleString('"__errors"')),
            cst.Arg(
                cst.Call(
                    func=cst.Name(validation_errors_function_name),
                    args=[cst.Arg(cst.Name("df"))],
                )
            ),
        ],
    )

    where_call = cst.Call(
        func=cst.Attribute(value=with_column_call, attr=cst.Name("where")),
        args=[
            cst.Arg(
                cst.BinaryOperation(
                    left=cst.Call(
                        func=cst.Name("size"),
                        args=[
                            cst.Arg(
                                cst.Call(
                                    func=cst.Name("col"),
                                    args=[cst.Arg(cst.SimpleString('"__errors"'))],
                                )
                            )
                        ],
                    ),
                    operator=cst.GreaterThan(),
                    right=cst.Integer("0"),
                )
            )
        ],
    )

    select_call = cst.Call(
        func=cst.Attribute(value=where_call, attr=cst.Name("select")),
        args=[cst.Arg(cst.SimpleString('"*"'))],
    )

    func = cst.FunctionDef(
        name=cst.Name(main_function_name),
        params=cst.Parameters(
            params=[
                cst.Param(
                    name=cst.Name("df"),
                    annotation=cst.Annotation(cst.Name("DataFrame")),
                )
            ]
        ),
        returns=cst.Annotation(cst.Name("DataFrame")),
        body=cst.IndentedBlock(
            [cst.SimpleStatementLine([cst.Return(value=select_call)])]
        ),
    )
    return func


def generate_validation_errors_function(
    model: type[BaseModel], function_name: str, column_names: list[str]
) -> cst.FunctionDef:
    column_names = [
        field_info.alias or field_name
        for field_name, field_info in model.model_fields.items()
    ]

    column_validation_function_calls = [
        cst.Call(
            func=cst.Name(column_validation_function_name(function_name, column_name)),
            args=[cst.Arg(cst.Name("df"))],
        )
        for column_name in column_names
    ]

    return_expr = cst.Call(
        func=cst.Name("flatten"),
        args=[
            cst.Arg(
                value=cst.Call(
                    func=cst.Name("array"),
                    args=[
                        cst.Arg(value=expr) for expr in column_validation_function_calls
                    ],
                )
            )
        ],
    )

    return cst.FunctionDef(
        name=cst.Name(function_name),
        params=cst.Parameters(
            params=[
                cst.Param(
                    name=cst.Name("df"),
                    annotation=cst.Annotation(cst.Name("DataFrame")),
                )
            ]
        ),
        returns=cst.Annotation(cst.Name("Column")),
        body=cst.IndentedBlock(
            [cst.SimpleStatementLine([cst.Return(value=return_expr)])]
        ),
    )


def generate_validation_column_function(
    function_name_prefix: str, column_name: str, field_info: FieldInfo
) -> cst.FunctionDef:
    function_name = column_validation_function_name(function_name_prefix, column_name)

    col_missing_condition = cst.UnaryOperation(
        operator=cst.Not(),
        expression=cst.Call(
            func=cst.Attribute(
                value=cst.Attribute(
                    value=cst.Name("df"),
                    attr=cst.Name("columns"),
                ),
                attr=cst.Name("__contains__"),
            ),
            args=[cst.Arg(cst.SimpleString(f'"{column_name}"'))],
        ),
    )

    # Error struct for missing required column:
    missing_required_column_error_struct = cst.Call(
        func=cst.Name("struct"),
        args=[
            cst.Arg(
                keyword=cst.Name("property"),
                value=cst.Call(
                    func=cst.Name("lit"),
                    args=[cst.Arg(cst.SimpleString(f'"/{column_name}"'))],
                ),
            ),
            cst.Arg(
                keyword=cst.Name("error"),
                value=cst.Call(
                    func=cst.Name("lit"),
                    args=[cst.Arg(cst.SimpleString('"required column is missing"'))],
                ),
            ),
        ],
    )

    # Return array([missing_column_error_struct])
    missing_column_return_stmt = cst.SimpleStatementLine(
        [
            cst.Return(
                value=cst.Call(
                    func=cst.Name("array"),
                    args=[cst.Arg(missing_required_column_error_struct)],
                )
            )
        ]
    )

    # Return array() empty
    empty_array_return_stmt = cst.SimpleStatementLine(
        [cst.Return(value=cst.Call(func=cst.Name("array"), args=[]))]
    )

    # If statement for missing column
    if_missing_col_stmt = cst.If(
        test=col_missing_condition,
        body=cst.IndentedBlock(
            [
                (
                    missing_column_return_stmt
                    if field_info.is_required()
                    else empty_array_return_stmt
                )
            ]
        ),
    )

    # TODO placeholder comment for continuing validation
    todo_comment = cst.EmptyLine(
        comment=cst.Comment(
            "# TODO: continue with null and other validation checks here"
        )
    )

    # Return an empty array at end to satisfy function signature (can be removed later)
    final_return_stmt = cst.SimpleStatementLine(
        [cst.Return(value=cst.Call(func=cst.Name("array"), args=[]))]
    )

    func_body = [
        if_missing_col_stmt,
        todo_comment,
        final_return_stmt,
    ]

    return cst.FunctionDef(
        name=cst.Name(function_name),
        params=cst.Parameters(
            params=[
                cst.Param(
                    name=cst.Name("df"),
                    annotation=cst.Annotation(cst.Name("DataFrame")),
                )
            ]
        ),
        returns=cst.Annotation(cst.Name("Column")),
        body=cst.IndentedBlock(func_body),
    )


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return name


def column_validation_function_name(prefix: str, column_name: str) -> str:
    suffix = to_snake_case(column_name)
    return f"{prefix}_for_column_{suffix}"
