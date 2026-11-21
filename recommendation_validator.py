from recommendation_models import RecommendationResponse, RuleRecommendation

def validate_recommendation_columns(recommendations: RecommendationResponse, column_metadata: dict) -> bool:
    for rule in recommendations.rules:
        if rule.column not in column_metadata:
            raise ValueError(f"Unknown column: {rule.column}")
    return True

def validate_recommendation_types(recommendations: RecommendationResponse,column_metadata: dict) -> bool:
    column_compatibility = {
            "positive": ["integer", 'float'],
            "not_null": ["string", "integer", "float", "date"]
    }
    
    for rule in recommendations.rules:

        # 1. Check whether the column exists
        if rule.column not in column_metadata:
            raise ValueError(
                f"Unknown column: {rule.column}"
            )

        # 2. Check whether the rule type is supported
        if rule.rule_type not in column_compatibility:
            raise ValueError(
                f"Unsupported rule type: {rule.rule_type}"
            )

        # 3. Get the column's data type
        data_type = column_metadata[rule.column].get("data_type")

        # 4. Check compatibility
        if data_type not in column_compatibility[rule.rule_type]:
            raise ValueError(
                f"Incompatible rule: {rule.rule_type} "
                f"cannot be applied to column '{rule.column}' "
                f"with data type '{data_type}'"
            )

    return True    

if __name__ == "__main__":

    column_metadata = {
        "amount": {"data_type": "float", "nullable": "no"},
        "transaction_date": {"data_type": "date", "nullable": "no"}
    }

    recommendations = RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="amount",
                rule_type="positive",
                reason="Amount must be positive."
            ),
            RuleRecommendation(
                column="transaction_date",
                rule_type="positive",
                reason="Transaction date must be positive."
            )
        ]
    )

    result = validate_recommendation_types(
        recommendations,
        column_metadata
    )
    
    print(f"Column validation results: {result}")

    response = validate_recommendation_columns(RecommendationResponse(
        rules=[
            RuleRecommendation(
                column="customer_age",
                rule_type="not_null",
                reason="Transaction can be a negative number."
        )])
                ,{"location_id": {
                                "data_type": "string",
                                "nullable": "no"
                                },
                "amount": {
                                "data_type": "date",
                                "nullable": "no"
                                }
                }
            )
    print(response)