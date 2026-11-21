from typing import Literal
import pytest
from rules import DataQualityRule
from engine import execute_rules


@pytest.mark.parametrize(
    "amount, expected",
    [
        (100, True),
        (0, False),
        (-50, False),
        (250.75, True)
    ]
)
def test_positive_rule(amount: float | Literal[100] | Literal[0] | Literal[-50], expected: bool):
    rule = DataQualityRule("amount", "positive")

    assert rule.validate(amount) == expected

def test_negative_number():
    rule = DataQualityRule("amount", "positive")

    result = rule.validate(-50)

    assert result is False

def test_null_value():
    rule = DataQualityRule("amount", "not_null")

    result = rule.validate(None)

    assert result is False

def test_unsupported_rule_type():

    with pytest.raises(ValueError):
        DataQualityRule("amount", "positve")

def test_invalid_field_name():
    with pytest.raises(ValueError):
        DataQualityRule(None, "positive")

@pytest.mark.parametrize(
    "customer_id, expected",
    [
        (5001, True),
        (None, False),
        ("", True),
        (0, True)
    ]
)

def test_not_null_parametrized(customer_id, expected):

    rule = DataQualityRule("customer_id", "not_null")

    assert rule.validate(customer_id) == expected

@pytest.fixture
def sample_transactions():
    return [
            {"transaction_id": 101, "amount": 100},
            {"transaction_id": 102, "amount": -50},
            {"transaction_id": 103, "amount": 0}
            ]

@pytest.fixture
def positive_rule():
    return [DataQualityRule("amount","positive")]

def test_execute_positive_rules_with_fixtures(sample_transactions: list[dict[str, int]], positive_rule: list[DataQualityRule]):
    expected_results = [{"transaction_id":101,"field_name":"amount", "status":"PASS", "message": None},
                        {"transaction_id":102,"field_name":"amount", "status":"FAIL", "message": "Value failed validation"},
                        {"transaction_id":103,"field_name":"amount", "status":"FAIL", "message": "Value failed validation"}
                        ]
    assert execute_rules(sample_transactions, positive_rule) == expected_results

def test_invalid_rule_type():
    with pytest.raises(ValueError, match="Unsupported rule type"):
        DataQualityRule("amount", "postive")