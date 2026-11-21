import pytest

from recommendation_models import RecommendationResponse, RuleRecommendation
from recommendation_validator import validate_recommendation_types


COLUMN_METADATA = {
    "amount": {"data_type": "float"},
    "transaction_id": {"data_type": "string"},
    "transaction_date": {"data_type": "date"}
}


@pytest.mark.parametrize(
    "rules, expected_error",
    [
        # Valid numeric rule
        (
            [("amount", "positive")],
            None
        ),

        # Valid not-null rule
        (
            [("transaction_id", "not_null")],
            None
        ),

        # Incompatible data type
        (
            [("transaction_date", "positive")],
            "Incompatible rule"
        ),

        # Unknown column
        (
            [("customer_age", "not_null")],
            "Unknown column"
        ),

        # First valid, second invalid
        (
            [
                ("amount", "positive"),
                ("transaction_date", "positive")
            ],
            "Incompatible rule"
        ),

        # Empty recommendations
        (
            [],
            None
        )
    ]
)
def test_validate_recommendation_types(rules, expected_error):

    recommendations = RecommendationResponse(
        rules=[
            RuleRecommendation(
                column=column,
                rule_type=rule_type,
                reason="Synthetic test recommendation"
            )
            for column, rule_type in rules
        ]
    )

    if expected_error is None:
        assert validate_recommendation_types(
            recommendations,
            COLUMN_METADATA
        ) is True

    else:
        with pytest.raises(ValueError, match=expected_error):
            validate_recommendation_types(
                recommendations,
                COLUMN_METADATA
            )