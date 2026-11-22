import pytest

from business_definition_models import BusinessDefinition
from business_definition_repository import (
    InMemoryBusinessDefinitionRepository
)


@pytest.fixture
def approved_definition():
    return BusinessDefinition(
        definition_id="NET_REVENUE",
        name="Net Revenue",
        version=1,
        description="Revenue after refunds",
        formula="Payments - Refunds",
        grain="Per location per day",
        rationale="Measure revenue after refunds",
        status="approved"
    )


def test_get_approved_definition(approved_definition):
    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition]
    )

    result = repo.get_approved("NET_REVENUE")

    assert result == approved_definition


def test_unknown_definition():
    repo = InMemoryBusinessDefinitionRepository([])

    assert repo.get_approved("UNKNOWN") is None


def test_draft_definition_excluded(approved_definition):
    approved_definition.status = "draft"

    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition]
    )

    assert repo.get_approved("NET_REVENUE") is None


def test_approved_version_selected_over_draft(approved_definition):
    draft = approved_definition.model_copy()
    draft.version = 2
    draft.status = "draft"

    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition, draft]
    )

    result = repo.get_approved("NET_REVENUE")

    assert result.version == 1
    assert result.status == "approved"


def test_multiple_approved_versions_rejected(approved_definition):
    second_version = approved_definition.model_copy()
    second_version.version = 2

    with pytest.raises(ValueError, match="Multiple approved versions"):
        InMemoryBusinessDefinitionRepository(
            [approved_definition, second_version]
        )


def test_input_mutation_does_not_affect_repository(approved_definition):
    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition]
    )

    approved_definition.formula = "Incorrect formula"

    assert repo.get_approved("NET_REVENUE").formula == "Payments - Refunds"


def test_output_mutation_does_not_affect_repository(approved_definition):
    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition]
    )

    result = repo.get_approved("NET_REVENUE")
    result.formula = "Incorrect formula"

    assert repo.get_approved("NET_REVENUE").formula == "Payments - Refunds"

def test_superseded_definition_excluded(approved_definition):
    approved_definition.status = "superseded"

    repo = InMemoryBusinessDefinitionRepository(
        [approved_definition]
    )

    assert repo.get_approved("NET_REVENUE") is None