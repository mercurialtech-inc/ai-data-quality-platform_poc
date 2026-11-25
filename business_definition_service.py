from business_definition_models import BusinessDefinition
from business_definition_repository import BusinessDefinitionRepository

class BusinessDefinitionService:

    def __init__(self, repository: BusinessDefinitionRepository):
        self._repository = repository

    def require_approved(self, definition_id: str) -> BusinessDefinition:
        
        definition = self._repository.get_approved(definition_id)

        if definition is None:
            raise LookupError(f"No definition found for {definition_id}")

        return definition