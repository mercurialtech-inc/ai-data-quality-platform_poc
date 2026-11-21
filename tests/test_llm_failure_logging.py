
import logging
from unittest.mock import patch

import pytest
from google.genai.errors import ClientError

from llm_recommender import recommend_rules


def test_gemini_api_failure_is_logged(caplog):
    fake_error = ClientError(
        429,
        {"error": {
            "code": 429,
            "message": "Rate limit exceeded"
        }}
    )

    with patch("llm_recommender.client.models.generate_content") as mock_api:
        mock_api.side_effect = fake_error

        with caplog.at_level(logging.ERROR):
            with pytest.raises(ClientError) as exc_info:
                recommend_rules("KPI_REVENUE_001")

    assert exc_info.value.code == 429

    failure_logs = [
    record for record in caplog.records
    if record.msg == "gemini_attempt_finished"
    and record.status == "error"
    ]

    assert len(failure_logs) == 1
    assert failure_logs[0].http_status == 429
    assert failure_logs[0].kpi_id == "KPI_REVENUE_001"
    assert failure_logs[0].status == "error"
