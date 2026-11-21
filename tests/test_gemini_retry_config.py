
from llm_recommender import GEMINI_HTTP_OPTIONS


def test_gemini_retry_configuration():

    options = GEMINI_HTTP_OPTIONS
    retry = options.retry_options

    assert options.timeout == 15000

    assert retry.attempts == 3
    assert retry.initial_delay == 1.0
    assert retry.max_delay == 4.0

    assert set(retry.http_status_codes) == {
        429, 500, 502, 503, 504
    }

    # Permanent request errors must not be retried.
    assert 400 not in retry.http_status_codes
    assert 401 not in retry.http_status_codes
    assert 403 not in retry.http_status_codes
