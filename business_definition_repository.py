from typing import Protocol
from business_definition_models import BusinessDefinition


class BusinessDefinitionRepository(Protocol):

    def get_approved(
        self, definition_id: str
    ) -> BusinessDefinition | None:
        ...

class InMemoryBusinessDefinitionRepository:

    def __init__(self, definitions: list[BusinessDefinition]):
        self._definitions: dict[str, BusinessDefinition] = {}

        for definition in definitions:

            if definition.status != "approved":
                continue

            if definition.definition_id in self._definitions:
                raise ValueError(
                    f"Multiple approved versions for "
                    f"{definition.definition_id}"
                )

            self._definitions[definition.definition_id] = (
                definition.model_copy(deep=True)
            )

    def get_approved(
        self, definition_id: str
    ) -> BusinessDefinition | None:

        definition = self._definitions.get(definition_id)

        if definition is None:
            return None

        return definition.model_copy(deep=True)