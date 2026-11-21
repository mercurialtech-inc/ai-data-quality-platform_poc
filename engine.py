
from rules import InvalidRuleDataError

def execute_rules(transactions, rules):
    results = []
    for transaction in transactions:
            for rule in rules:
                if rule.field_name in transaction:
                    
                    try:
                        value = transaction[rule.field_name]
                        is_valid = rule.validate(value)
                        status = "PASS" if is_valid else "FAIL"
                        message = None if is_valid else "Value failed validation"
                    
                    except InvalidRuleDataError:
                        status = "ERROR"
                        message = "Invalid data type for rule"
                else:
                     status = "ERROR"
                     message = f"Field '{rule.field_name}' is missing"
                
                final_op = {
                     "transaction_id":transaction["transaction_id"],
                     "field_name":rule.field_name,
                     "status":status,
                     "message": message
                }
                results.append(final_op)
    return results