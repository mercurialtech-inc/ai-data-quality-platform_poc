
import json
import logging
import pytest

from logging_config import JSONFormatter


@pytest.mark.parametrize(
    "extra, expected",
    [
        (
            {
                "kpi_id": "KPI_REVENUE_001",
                "model": "gemini-test",
                "latency_ms": 1250.45,
                "status": "success",
            },
            {
                "kpi_id": "KPI_REVENUE_001",
                "model": "gemini-test",
                "latency_ms": 1250.45,
                "status": "success",
            },
        ),
        (
            {},
            {
                "kpi_id": None,
                "model": None,
                "latency_ms": None,
                "status": None,
            },
        ),
    ],
)
def test_json_formatter(extra, expected):
    logger = logging.getLogger("test_recommender")

    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn=__file__,
        lno=1,
        msg="gemini_request_completed",
        args=(),
        exc_info=None,
        extra=extra,
    )

    formatter = JSONFormatter()
    result = formatter.format(record)

    log_data = json.loads(result)

    assert log_data["level"] == "INFO"
    assert log_data["logger"] == "test_recommender"
    assert log_data["event"] == "gemini_request_completed"
    assert "timestamp" in log_data

    for field, value in expected.items():
        assert log_data[field] == value
