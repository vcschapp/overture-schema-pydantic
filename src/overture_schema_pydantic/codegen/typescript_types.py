from pydantic import BaseModel

from pydantic2ts import generate_typescript_defs

# Some minor annoyances with this tool:
#    1. Input/output is files, so there's less ability to control the UX.
#    2. Requires `json-schema-to-typescript` or fails with an error. Which means it has external
#       dependencies on NPM being there and specific tools being installed.
#
# Some MAJOR annoyances:
#    Once I got through the major annoyances, I ran the below program, which crashed with the error:
#    `TypeError: unhashable type: 'dict'`. Given how simple this Pydantic schema is so far, I deem
#    this tool unworthy of serious consideration.
#
# Program I ran:
#
# ```
# $ poetry run python
# Python 3.12.3 (main, May 26 2025, 18:50:19) [GCC 13.3.0] on linux
# Type "help", "copyright", "credits" or "license" for more information.
# >>> from overture_schema_pydantic.codegen.typescript_types import generate_code
# >>> generate_code()
# ```

def generate_code():
    generate_typescript_defs("overture_schema_pydantic.divisions", "division.ts")
