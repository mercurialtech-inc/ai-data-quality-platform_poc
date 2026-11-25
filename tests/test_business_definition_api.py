
from fastapi.testclient import TestClient

from api import app, get_business_definition_service
from business_definition_repository import InMemoryBusinessDefinitionRepository
from business_definition_service import BusinessDefinitionService


def test_get_definition_returns_404_when_missing():

    # 1. Create an empty in-memory repository
    repo = InMemoryBusinessDefinitionRepository([])

    # 2. Create a service using that repository
    service = BusinessDefinitionService(repo)

    # 3. Define a replacement dependency provider
    def fake_service():
        return service

    # 4. Tell FastAPI to use our replacement
    app.dependency_overrides[get_business_definition_service] = fake_service

    try:
        # 5. Simulate an HTTP request
        client = TestClient(app)
        response = client.get("/definitions/UNKNOWN_KPI")

        # 6. Verify HTTP response
        assert response.status_code == 404
        assert response.json() == {
            "detail": "No approved definition found for UNKNOWN_KPI"
        }

    finally:
        # 7. Restore the original dependency configuration
        app.dependency_overrides.clear()
