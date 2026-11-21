from dataclasses import dataclass


@dataclass
class RejectedRule:
    field_name: str
    rule_type: str
    reason: str