
class InvalidRuleDataError(ValueError):
    pass

def check_not_null(value: object) -> bool:
        if value is None:
            return False

        return True

def check_positive(value: int | float | None) -> bool:
        if not isinstance(value, (int, float)):
            raise InvalidRuleDataError("Amount must be numeric")
        
        return value > 0


class DataQualityRule:
    def __init__(self, field_name: str, rule_type: str) -> None:
        
        valid_rule_types = ["positive", "not_null"]
        
        if rule_type not in valid_rule_types:
            raise ValueError(f"Unsupported rule type: {rule_type}")

        if not isinstance(field_name, str) or field_name.strip() == "":
            raise ValueError("Field name cannot be empty")
        
        self.field_name = field_name
        self.rule_type = rule_type

    def validate(self, value: int | float | str | None) -> bool:
        if self.rule_type == "not_null":
            return check_not_null(value)
        
        if self.rule_type == "positive":
            return check_positive(value)

        raise ValueError("Unsupported rule type")
