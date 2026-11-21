from unittest.mock import patch
import pytest
from recommendation_models import (
    RecommendationResponse,
    RuleRecommendation
)
from recommendation_service import generate_validated_recommendations


def test_generate_validated_recommendations():

    fake_recommendations = RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="transaction_id",
                rule_type="not_null",
                reason="Transaction ID is required."
            )
        ]
    )

    with patch("recommendation_service.recommend_rules") as mock_llm:

        mock_llm.return_value = fake_recommendations

        result = generate_validated_recommendations(
            "KPI_REVENUE_001",
            "Refund amounts may be negative."
        )

        assert result == fake_recommendations

        mock_llm.assert_called_once_with(
            "KPI_REVENUE_001",
            "Refund amounts may be negative."
        )


def test_service_rejects_incompatible_rule():

    invalid_recommendations = RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="transaction_date",
                rule_type="positive",
                reason="Transaction dates must be positive."
            )
        ]
    )

    with patch("recommendation_service.recommend_rules") as mock_llm:

        mock_llm.return_value = invalid_recommendations

        with pytest.raises(ValueError, match="Incompatible rule"):
            generate_validated_recommendations(
                "KPI_REVENUE_001",
                "Refund amounts may be negative."
            )

        mock_llm.assert_called_once_with(
            "KPI_REVENUE_001",
            "Refund amounts may be negative."
        )