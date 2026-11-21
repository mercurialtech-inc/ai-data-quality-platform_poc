from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import Literal

class RuleConfig(BaseModel):
    field_name: str = Field(min_length=1)
    rule_type: Literal["positive", "not_null"]

    @field_validator("field_name")
    def validate_field_type(cls, field_name):
        if field_name.strip() == "":
            raise ValueError("Unsupported rule type")
        
        return field_name

try:
    rule = RuleConfig(field_name="amount", rule_type="positive")
except ValueError as e:
    print(e)

class RulePreviewRequest(BaseModel):
    rules: list[RuleConfig] = Field(min_length=1)
    transactions: list[dict[str, int | float | str | None]]

class HealthResponse(BaseModel):
    status: str
    service: str

class RuleResult(BaseModel):
    transaction_id: int
    field_name: str
    status: Literal["PASS", "FAIL", "ERROR"]
    message: str | None

class SummaryResponse(BaseModel):
    total: int
    passed: int 
    failed: int
    errors: int
    unknown:int 
    unknown_statuses: list[str]
    summary_status: str

class RulePreviewResponse(BaseModel):
    results: list[RuleResult]
    summary: SummaryResponse

#rule = RuleConfig(field_name="amount", rule_type="positive")
#print(rule.field_name)
#print(rule.model_dump())