from recommendation_models import RecommendationResponse
from kpi_catalog import get_kpi_metadata
from llm_recommender import recommend_rules
from recommendation_validator import validate_recommendation_columns, validate_recommendation_types

def generate_validated_recommendations(kpi_id: str,business_context: str | None = None) -> RecommendationResponse:
    _, all_column_meta, _ = get_kpi_metadata(kpi_id)
    recommendation = recommend_rules(kpi_id, business_context)
    validate_recommendation_columns(recommendation, all_column_meta)
    validate_recommendation_types(recommendation, all_column_meta)

    return recommendation

if __name__ == "__main__":
    response = generate_validated_recommendations("KPI_REVENUE_001","Refund amounts may be negative.")
    print(f"Valid recommendation generateed: {response}")

