import pytest
from recommendation_models import RecommendationResponse, RuleRecommendation
from recommendation_validator import validate_recommendation_columns

def test_recommendation_validator():
        
    response=RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="customer_age",
                rule_type="not_null",
                reason="Transaction can be a negative number."
        )])
    column_metadata= {"location_id": {
                                "data_type": "string",
                                "nullable": "no"
                                },
                "amount": {
                                "data_type": "date",
                                "nullable": "no"
                                }
                }
    
    with pytest.raises(ValueError, match="Unknown column: customer_age"):
        validate_recommendation_columns(response, column_metadata)

def test_valid_recommendation_columns():
    response=RecommendationResponse(
            rules=[
                RuleRecommendation(
                    column="amount",
                    rule_type="positive",
                    reason="Amount should be positive."
            ),
             RuleRecommendation(
                                column="transaction_id",
                                rule_type="not_null",
                                reason="Transaction cannot be null."
                        )
            ])
    column_metadata= {"transaction_id": {
                                    "data_type": "string",
                                    "nullable": "no"
                                    },
                    "amount": {
                                    "data_type": "string",
                                    "nullable": "no"
                                    }
                    }
    assert validate_recommendation_columns(response, column_metadata) == True