from typing import Annotated, Literal
from pydantic import BaseModel, Field, StringConstraints


NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1)
]


class BusinessDefinition(BaseModel):
    definition_id: NonEmptyString
    name: NonEmptyString
    version: int = Field(ge=1, strict=True)
    description: NonEmptyString
    formula: NonEmptyString
    grain: NonEmptyString
    rationale: NonEmptyString
    status: Literal["draft", "approved", "superseded"] = "draft"