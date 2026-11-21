
import logging
from unittest.mock import MagicMock, patch

import pytest

from llm_recommender import recommend_rules


def test_gemini_response_validation_failure(caplog):

    # Simulate an API response with invalid parsed output
    fake_response = MagicMock()
    fake_response.parsed = None

    with patch(
        "llm_recommender.client.models.generate_content",
        return_value=fake_response
    ) as mock_api:

        with caplog.at_level(logging.ERROR):

            with pytest.raises(RuntimeError, match="Gemini did not return"):
                recommend_rules("KPI_REVENUE_001")

    # Verify Gemini was called once
    mock_api.assert_called_once()

    # Find our application-specific validation failure log
    failure_logs = [
    record for record in caplog.records
    if record.msg == "gemini_attempt_finished"
    and record.status == "error"
    and record.error_type == "InvalidStructuredResponse"
    ]

    assert len(failure_logs) == 1

    failure = failure_logs[0]

    assert failure.levelname == "ERROR"
    assert failure.kpi_id == "KPI_REVENUE_001"
    assert failure.status == "error"
    assert failure.error_type == "InvalidStructuredResponse"
