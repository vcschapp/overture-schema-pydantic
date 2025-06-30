from pydantic import BaseModel

from pydantic2zod import Compiler


def generate_code() -> str:
    return Compiler().parse("overture_schema_pydantic.divisions").to_zod()
