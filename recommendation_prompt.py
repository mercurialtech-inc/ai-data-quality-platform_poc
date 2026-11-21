from recommendation_context import build_recommendation_context
import json


def build_recommendation_prompt(context: dict) -> str: 
    #business_context = build_recommendation_context(context)

    prompt_text =  f"""You are assisting with data quality rule recommendations.

            Recommend candidate data quality rules based on the
            provided KPI definition and column metadata.

            **KPI Metadata:**
            {json.dumps(context["kpi"])}

            **Column Metadata:**
            {json.dumps(context["columns"])}

            Additional Business Context:
            {json.dumps(context["business_context"])}

            Supported rule types:
            - positive
            - not_null

            Only recommend rules that are supported by the provided
            information.

            Explain the business reasoning for each recommendation.

            Do not invent missing business requirements.

            If the available context does not justify a rule,
            do not recommend it.

            Your recommendations are proposals requiring human review.
        """
    

    return prompt_text

if __name__ == "__main__":
    context = build_recommendation_context(
        "KPI_REVENUE_001",
        "Refund amounts may be negative."
    )

    prompt = build_recommendation_prompt(context)

    print(prompt)