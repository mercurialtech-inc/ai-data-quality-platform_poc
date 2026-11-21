from google import genai
from google.genai import types
from google.genai.errors import APIError
import os
import time
from recommendation_models import RecommendationResponse
from recommendation_context import build_recommendation_context
from recommendation_prompt import build_recommendation_prompt
import logging
from logging_config import configure_logging

logger = logging.getLogger(__name__)

GEMINI_HTTP_OPTIONS = types.HttpOptions(
    timeout=15000,
    retry_options=types.HttpRetryOptions(
        attempts=3,
        initial_delay=1.0,
        max_delay=4.0,
        http_status_codes=[429, 500, 502, 503, 504]
    )
)

client = genai.Client(http_options=GEMINI_HTTP_OPTIONS)


def recommend_rules(
    kpi_id: str,
    business_context: str | None = None
) -> RecommendationResponse:

    logger.debug("Building context")
    context = build_recommendation_context(kpi_id, business_context)

    logger.debug("Constructing prompt")
    prompt_text = build_recommendation_prompt(context)

    model = os.getenv("GEMINI_MODEL")

    status = "error"
    error_type = None
    http_status = None
    usage = None

    logger.info("Sending request to Gemini")
    start = time.perf_counter()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecommendationResponse
            )
        )

        usage = response.usage_metadata

        if not isinstance(response.parsed, RecommendationResponse):
            error_type = "InvalidStructuredResponse"
            raise RuntimeError(
                "Gemini did not return a valid RecommendationResponse"
            )

        status = "success"
        return response.parsed

    except APIError as error:
        error_type = type(error).__name__
        http_status = error.code
        raise

    except Exception as error:
        if error_type is None:
            error_type = type(error).__name__
        raise

    finally:
        elapsed_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        logger.log(
            logging.INFO if status == "success" else logging.ERROR,
            "gemini_attempt_finished",
            extra={
                "kpi_id": kpi_id,
                "model": model,
                "latency_ms": elapsed_ms,
                "input_tokens": getattr(
                    usage, "prompt_token_count", None
                ),
                "output_tokens": getattr(
                    usage, "candidates_token_count", None
                ),
                "thinking_tokens": getattr(
                    usage, "thoughts_token_count", None
                ),
                "total_tokens": getattr(
                    usage, "total_token_count", None
                ),
                "status": status,
                "error_type": error_type,
                "http_status": http_status
            }
        )

    
 
if __name__ == "__main__":

    configure_logging()

    response = recommend_rules("KPI_REVENUE_001","Refund amounts may be negative.")

    print(response)