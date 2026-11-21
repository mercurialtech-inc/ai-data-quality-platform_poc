from recommendation_models import RecommendationResponse
from recommendation_models import RuleRecommendation

def evaluate_refund_recommendations(recommendations: RecommendationResponse) -> bool:
    for rule in recommendations.rules:
        if rule.column == "amount" and rule.rule_type == "positive":
            return False
        
    return True

if __name__ == "__main__":

    recommendations = RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="transaction_id",
                rule_type="not_null",
                reason="Transaction ID cannot be null."
            ),
            RuleRecommendation(
                column="location_id",
                rule_type="not_null",
                reason="Location ID is required."
            ),
            RuleRecommendation(
                column="transaction_date",
                rule_type="not_null",
                reason="Transaction date is required."
            )
        ]
    )

    result = evaluate_refund_recommendations(recommendations)
    print(result)