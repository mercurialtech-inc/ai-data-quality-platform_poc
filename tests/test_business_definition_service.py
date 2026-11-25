from business_definition_models import BusinessDefinition
from business_definition_repository import InMemoryBusinessDefinitionRepository
from business_definition_service import BusinessDefinitionService


def test_require_approved_returns_definition():
    definition = BusinessDefinition(
        definition_id="TEST_NET_REVENUE",
        version=1,
        name="Test Net Revenue",
        description="Synthetic definition",
        formula="Payments - Refunds",
        grain="Location/day",
        rationale="Unit test",
        status="approved"
    )

    repository = InMemoryBusinessDefinitionRepository([definition])
    service = BusinessDefinitionService(repository)

    result = service.require_approved("TEST_NET_REVENUE")

    assert result.definition_id == "TEST_NET_REVENUE"
    assert result.version == 1
    assert result.status == "approved"

import pytest

def test_require_approved_raises_when_missing():

    # Create an empty repository (no business definitions)
    repository = InMemoryBusinessDefinitionRepository([])

    # Inject the repository into our service
    service = BusinessDefinitionService(repository)

    # Verify that the service raises LookupError
    with pytest.raises(LookupError, match="UNKNOWN_KPI"):
        service.require_approved("UNKNOWN_KPI")