from engine import execute_rules
from rules import DataQualityRule

transactions = [
    {"transaction_id": 101, "customer_id": 5001, "amount": 250},
    {"transaction_id": 102, "customer_id": 5002, "amount": -50},
    {"transaction_id": 104, "customer_id": 5004}
]

expected_results = [
    {"transaction_id": 101, "field_name": "amount", "status": "PASS", "message":None},
    {"transaction_id": 101, "field_name": "customer_id", "status": "PASS", "message":None},
    {"transaction_id": 102, "field_name": "amount", "status": "FAIL", "message":"Value failed validation"},
    {"transaction_id": 102, "field_name": "customer_id", "status": "PASS", "message":None},
    {"transaction_id": 104, "field_name": "amount", "status": "ERROR", "message":"Field 'amount' is missing"},
    {"transaction_id": 104, "field_name": "customer_id", "status": "PASS", "message":None}
]

amount_rule = DataQualityRule("amount", "positive")
customer_rule = DataQualityRule("customer_id", "not_null")

rules = [amount_rule, customer_rule]

expected_count = len(transactions) * len(rules)


def test_execute_rules():
    engine_op = execute_rules(transactions, rules) 

    print("Actual engine results:", engine_op)
    assert engine_op == expected_results
    assert len(engine_op) == expected_count

def test_invalid_amount_type():
    transactions = [
    {"transaction_id": 105, "customer_id": 5005, "amount": "UNKNOWN"},
    {"transaction_id": 106, "customer_id": None, "amount": 150}
    ]

    engine_op = execute_rules(transactions, rules)

    expected_results = [
        {"transaction_id": 105, "field_name": "amount", "status": "ERROR", "message": "Invalid data type for rule"},
        {"transaction_id": 105, "field_name": "customer_id", "status": "PASS", "message": None},
        {"transaction_id": 106, "field_name": "amount", "status": "PASS", "message": None},
        {"transaction_id": 106, "field_name": "customer_id", "status": "FAIL", "message": "Value failed validation"}
    ]

    assert engine_op == expected_results



