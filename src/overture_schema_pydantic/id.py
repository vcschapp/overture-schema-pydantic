from typing import Annotated
from pydantic import Field

Id = Annotated[
    str,
    Field(
        min_length=1,
        pattern=r"^(\S.*)?\S$",
        description="A feature ID. This may be an ID associated with "
        "the Global Entity Reference System (GERS) "
        "if-and-only-if the feature represents an entity "
        "that is part of GERS.",
    ),
]
