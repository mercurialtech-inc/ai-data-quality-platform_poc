import pytest
from recommendation_models import RecommendationResponse, RuleRecommendation
from recommendation_evaluation import evaluate_refund_recommendations

@pytest.mark.parametrize(
    "recommendations, expected",
    [
        (RecommendationResponse(rules=[RuleRecommendation(column="amount",rule_type="positive"
                                        ,reason="The transaction to switch on the machine should always be positive")]), False),
        (RecommendationResponse(rules=[RuleRecommendation(column= "transaction_id",rule_type="not_null"
                                        ,reason="Transaction ID cannot be null as its unique transaction id")]), True),
        (RecommendationResponse(rules=[]), True),
        (RecommendationResponse(
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
                column="amount",
                rule_type="positive",
                reason="The transaction to switch on the machine should always be positive"
            )]),False)
    ]
)
def test_evaluate_refund_recommendations(recommendations, expected):
    result = evaluate_refund_recommendations(recommendations)
    assert result == expected