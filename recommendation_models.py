from pydantic import BaseModel
from typing import Literal

class RuleRecommendation(BaseModel):
    column: str
    rule_type: Literal["positive", "not_null"]
    reason: str

class RecommendationResponse(BaseModel):
    rules: list[RuleRecommendation]

class RecommendationRequest(BaseModel):
    kpi_id: str
    business_context: str | None = None
