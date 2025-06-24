import re

from pydantic_core import core_schema

BCP_47_REGEX = re.compile(
    r"^(?:(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}?)|(?:[A-Za-z]{4,8}))(?:-[A-Za-z]{4})?(?:-[A-Za-z]{2}|[0-9]{3})?(?:-(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(?:-[A-WY-Za-wy-z0-9](?:-[A-Za-z0-9]{2,8})+)*$"
)


class LanguageTag(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source, handler):
        return core_schema.str_schema(
            min_length=2,
            pattern=BCP_47_REGEX.pattern,
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(
            description="BCP-47 language tag", examples=["en", "en-US", "zh-Hant"]
        )
        return schema
