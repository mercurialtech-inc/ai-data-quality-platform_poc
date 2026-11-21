from recommendation_models import RuleRecommendation, RecommendationResponse

first_rule = RuleRecommendation(
                            column="amount"
                            ,rule_type="positive"
                            ,reason="The transaction to switch on the machine should always be positive")
second_rule = RuleRecommendation(
                            column= "transaction_id"
                            ,rule_type="not_null"
                            ,reason="Transaction ID cannot be null as its unique transaction id")

dq_rules = RecommendationResponse(rules=[first_rule, second_rule])

print(dq_rules.model_dump())

print(dq_rules.model_dump_json())