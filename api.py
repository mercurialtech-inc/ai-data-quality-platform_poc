from fastapi import FastAPI, HTTPException, Request
from schemas import RuleConfig, RulePreviewRequest,HealthResponse, RulePreviewResponse
from service import run_checks
from rules import DataQualityRule
from recommendation_models import RecommendationResponse, RecommendationRequest
from recommendation_service import generate_validated_recommendations
from request_context import request_id_var
import uuid
from logging_config import configure_logging

app = FastAPI()
configure_logging()

@app.middleware("http")
async def define_context(request: Request, call_next):
    
    u_id = str(uuid.uuid4())
    request_id = request_id_var.set(u_id) 

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = u_id
    finally:
        
        request_id_var.reset(request_id)

    return response

@app.get("/health", response_model=HealthResponse)
def get_health():
    return {
    "status": "ok",
    "service": "data-quality-api"
}

@app.post("/rules/validate")
def validate_rule(rule: RuleConfig):
    return {
    "status": "valid",
    "field_name": rule.field_name,
    "rule_type": rule.rule_type
    } 

@app.post("/rules/preview", response_model=RulePreviewResponse)
def rules_preview(preview_rule: RulePreviewRequest):
    
    rules = []
    for rule in preview_rule.rules:
        dq_rule = DataQualityRule(rule.field_name, rule.rule_type)
        rules.append(dq_rule)

    transactions = preview_rule.transactions

    if len(transactions) == 0:
        raise HTTPException(
            status_code=400,
            detail="Transactions can't be empty"
        )

    return run_checks(transactions, rules)

@app.post("/rules/recommend", response_model=RecommendationResponse)
def recommend_rules_endpoint(request: RecommendationRequest):
    try:
        return generate_validated_recommendations(request.kpi_id, request.business_context)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Key id {request.kpi_id} not found"
        )