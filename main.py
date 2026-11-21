from rules import DataQualityRule
from models import RejectedRule
from service import run_checks
import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def main():
    #raise RuntimeError("Simulated database connection failure")

    transactions = [
    {"transaction_id": 101, "customer_id": 5001, "amount": 250},
    {"transaction_id": 102, "customer_id": 5002, "amount": -50},
    {"transaction_id": 104, "customer_id": 5004},
    {"transaction_id": 103, "customer_id": None, "amount": None},
    {"transaction_id": 105,"customer_id": 5005, "amount": "UNKNOWN"}
    ]

    rule_configs = [
    ("amount", "postive"),      # Typo - will raise error
    ("customer_id", "not_null"), # Valid - will succeed
    ("", "positive"), # Will Fail Empty field error
    ("amount", "positive") # Valid - will succeed
    ]

    rules = []
    rejected_rules = []

    for field, r_type in rule_configs:
        try:
            # Try creating the rule
            rule = DataQualityRule(field, r_type)
            rules.append(rule)
        
        except ValueError as e:
            rejected_rules.append(RejectedRule(field, r_type, str(e)))
            # If it fails, catch it, logging a warning, and 'continue' to the next loop item
            logger.warning("Skipping rule for: %s: %s",field, e)

    # Now run the engine with whatever valid rules survived
    dq_response = run_checks(transactions, rules)
    
    print("The results are:", dq_response["results"])
    print("The summary is:", dq_response["summary"])

    if len(rejected_rules) > 0:
       print("Rules that failed are:", rejected_rules)
    else:
        print("All rule configurations accepted")



if __name__ == "__main__":
    try:
        main()
    except:
        logger.exception("Unexpected DQ application failure")
        sys.exit(1)