import pytest
from summary import summarize_results

def test_summarize_results():
    results = [
        {"status": "PASS"},
        {"status": "FAIL"},
        {"status": "ERROR"},
        {"status": "PASSED"},
        {"status": "PASSED"},
        {"status": "SKIPPED"}
    ]

    final_result = summarize_results(results)

    assert final_result == {
                                "total": 6,
                                "passed": 1,
                                "failed": 1,
                                "errors": 1,
                                "unknown": 3,
                                "unknown_statuses": ["PASSED", "SKIPPED"],
                                "summary_status": "INCOMPLETE"
                            }