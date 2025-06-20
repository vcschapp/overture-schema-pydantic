from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Source(BaseModel):
    # TODO: Property should be validated as a syntactically JSON Pointer using a field validator,
    #       and the entire feature should have an @model_validator that walks the JSON pointer to
    #       ensure it points somewhere valid.
    property: str
    dataset: str
    record_id: Optional[str] = None
    update_time: Optional[datetime] = None
    confidence: Optional[float] = None
