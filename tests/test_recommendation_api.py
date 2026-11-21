from unittest.mock import patch
from fastapi.testclient import TestClient
from api import app
from recommendation_models import RuleRecommendation, RecommendationResponse, RecommendationRequest

client = TestClient(app)

def test_recommend_rules_api():
    recommentaion = RuleRecommendation(column='transaction_id', rule_type='not_null', reason='The transaction_id column metadata explicitly states that it is not nullable.')
    test_recommendations = RecommendationResponse(rules=[recommentaion])
    
    with patch("api.generate_validated_recommendations") as mock_recommendation:
        mock_recommendation.return_value = test_recommendations

        response = client.post(
            "/rules/recommend",
            json={"kpi_id": "KPI_REVENUE_001",
                "business_context": "Transaction ID is required to identify each transaction."
                }
        )

        assert response.status_code == 200
        assert response.json()["rules"][0]["column"]  == "transaction_id"
        assert response.json()["rules"][0]["rule_type"]  == "not_null"

        mock_recommendation.assert_called_once_with("KPI_REVENUE_001",
             "Transaction ID is required to identify each transaction.")


def test_recommend_rules_unknown_kpi():

    with patch("api.generate_validated_recommendations") as mock_service:

        mock_service.side_effect = KeyError("KPI_UNKNOWN_999")

        response = client.post(
            "/rules/recommend",
            json={
                "kpi_id": "KPI_UNKNOWN_999",
                "business_context": None
            }
        )

        assert response.status_code == 404

        assert response.json()["detail"] == (
            "Key id KPI_UNKNOWN_999 not found"
        )

        mock_service.assert_called_once_with(
            "KPI_UNKNOWN_999",
            None
        )