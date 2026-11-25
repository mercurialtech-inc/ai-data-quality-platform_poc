from typing import Protocol
from business_definition_models import BusinessDefinition
from sqlalchemy import select
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import Session
from database_models import BusinessDefinitionORM




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

class PostgreSQLBusinessDefinitionRepository:

    def __init__(self, engine: Engine | Connection):
        self._engine = engine

    def get_approved(
        self, definition_id: str
    ) -> BusinessDefinition | None:

        with Session(self._engine) as session:

            statement = select(BusinessDefinitionORM).where(
                BusinessDefinitionORM.definition_id == definition_id,
                BusinessDefinitionORM.status == "approved"
            )

            record = session.execute(
                statement
            ).scalar_one_or_none()

            if record is None:
                return None

            return BusinessDefinition.model_validate(
                record,
                from_attributes=True
            )

    def save_draft(self, definition: BusinessDefinition) -> None:

        if definition.status != "draft":
            raise ValueError("Only draft definitions can be saved")

        with Session(self._engine) as session:
            with session.begin():
                record = BusinessDefinitionORM(
                **definition.model_dump()
            )
                session.add(record)

