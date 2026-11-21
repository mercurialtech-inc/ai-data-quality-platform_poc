
import logging
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from llm_recommender import recommend_rules


def test_invalid_response_preserves_token_usage(caplog):
    fake_response = SimpleNamespace(
        parsed=None,
        usage_metadata=SimpleNamespace(
            prompt_token_count=300,
            candidates_token_count=120,
            thoughts_token_count=None,
            total_token_count=420,
        ),
    )

    with patch(
        "llm_recommender.client.models.generate_content",
        return_value=fake_response,
    ) as mock_api:

        with caplog.at_level(logging.INFO):
            with pytest.raises(
                RuntimeError,
                match="Gemini did not return a valid RecommendationResponse",
            ):
                recommend_rules("KPI_REVENUE_001")

    mock_api.assert_called_once()

    failure_logs = [
    record for record in caplog.records
    if record.msg == "gemini_attempt_finished"
    and record.status == "error"
    ]

    success_logs = [
        record for record in caplog.records
        if record.msg == "gemini_request_completed"
    ]

    assert len(failure_logs) == 1
    assert len(success_logs) == 0

    failure = failure_logs[0]

    assert failure.levelname == "ERROR"
    assert failure.status == "error"
    assert failure.input_tokens == 300
    assert failure.output_tokens == 120
    assert failure.thinking_tokens is None
    assert failure.total_tokens == 420
