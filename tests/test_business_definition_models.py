import pytest
from pydantic import ValidationError
from business_definition_models import BusinessDefinition


@pytest.fixture
def valid_definition():
    return {
        "definition_id": "GROSS_REVENUE",
        "name": "Gross Revenue",
        "version": 1,
        "description": "Total successful customer payments",
        "formula": "Sum of successful payments before refunds",
        "grain": "Per location per day",
        "rationale": "Measure sales before deductions"
    }


def test_valid_definition(valid_definition):
    definition = BusinessDefinition(**valid_definition)

    assert definition.definition_id == "GROSS_REVENUE"
    assert definition.version == 1
    assert definition.formula == valid_definition["formula"]


def test_default_status(valid_definition):
    definition = BusinessDefinition(**valid_definition)

    assert definition.status == "draft"


def test_approved_status(valid_definition):
    valid_definition["status"] = "approved"

    definition = BusinessDefinition(**valid_definition)

    assert definition.status == "approved"


@pytest.mark.parametrize("version", [0, -1, "1", 1.5, True])
def test_invalid_version(valid_definition, version):
    valid_definition["version"] = version

    with pytest.raises(ValidationError):
        BusinessDefinition(**valid_definition)


def test_invalid_status(valid_definition):
    valid_definition["status"] = "pending"

    with pytest.raises(ValidationError):
        BusinessDefinition(**valid_definition)


@pytest.mark.parametrize("field", [
    "definition_id",
    "name",
    "description",
    "formula",
    "grain",
    "rationale"
])
@pytest.mark.parametrize("value", ["", "   "])
def test_blank_fields(valid_definition, field, value):
    valid_definition[field] = value

    with pytest.raises(ValidationError):
        BusinessDefinition(**valid_definition)


def test_whitespace_stripping(valid_definition):
    valid_definition["name"] = "  Gross Revenue  "

    definition = BusinessDefinition(**valid_definition)

    assert definition.name == "Gross Revenue"