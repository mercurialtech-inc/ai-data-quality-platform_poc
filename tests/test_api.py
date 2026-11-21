from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_preview_positive_rule():
    response = client.post("/rules/preview",
                           json={
                                "rules": [
                                            {"field_name": "amount", "rule_type": "positive"},
                                            {"field_name": "customer_id", "rule_type": "not_null"}
                                        ],
                                "transactions": [
                                    {"transaction_id": 101, "amount": 200, "customer_id": 501},
                                    {"transaction_id": 102, "amount": -50, "customer_id": None}
                                ]
                            } 
                            )

    assert response.status_code == 200
    assert response.json() == {
                                        "results": [
                                                    {
                                                    "transaction_id": 101,
                                                    "field_name": "amount",
                                                    "status": "PASS",
                                                    "message": None
                                                    },
                                                    {
                                                    "transaction_id": 101,
                                                    "field_name": "customer_id",
                                                    "status": "PASS",
                                                    "message": None
                                                    },
                                                    {
                                                    "transaction_id": 102,
                                                    "field_name": "amount",
                                                    "status": "FAIL",
                                                    "message": "Value failed validation"
                                                    },
                                                    {
                                                    "transaction_id": 102,
                                                    "field_name": "customer_id",
                                                    "status": "FAIL",
                                                    "message": "Value failed validation"
                                                    }
                                                ],
                                        "summary": {
                                                        "total": 4,
                                                        "passed": 2,
                                                        "failed": 2,
                                                        "errors": 0,
                                                        "unknown": 0,
                                                        "unknown_statuses": [],
                                                        "summary_status": "COMPLETE"
                                                    }
                                }
    
def test_preview_invalid_rule_type():
    response = client.post("/rules/preview",
                           json={
                                "rules": [
                                    {
                                    "field_name": "amount",
                                    "rule_type": "postive"
                                    }
                                ],
                                "transactions": [
                                    {"transaction_id": 201, "amount": 100}
                                ]
                                }
                            )

    assert response.status_code == 422
   # invalid_rule = response.json()
    assert response.json()["detail"][0]["loc"] ==  [
        "body",
        "rules",
        0,
        "rule_type"
      ]
