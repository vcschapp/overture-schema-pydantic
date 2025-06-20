POC goals

1) ~~Model geometry.~~
2) ~~Model an arbitrary custom constraint. (Geometry type)~~
3) Model feature type.
4) Override JSON Schema production either using `__get_pydantic_json_schema__` or by overriding `BaseModel.model_json_schema`.
5) ~~Generate a typed ID reference.~~
6) Model common names with language tags as dictionary keys.
7) Model sources with JSON Pointer value.
8) Annotate `int` type with a "hard range" annotation for Parquet.
9) Figure out how this would propagate through Spark into Parquet file.
10) Generate a Spark schema.

Some observations of base types needed:

- A non-empty string type that has no leading or trailing whitespace.
- A floating-point number [0,1] representing a percentage, used for both
  confidence and linear referencing.
