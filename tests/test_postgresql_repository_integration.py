
import pytest
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from database import engine
from database_models import BusinessDefinitionORM
from business_definition_models import BusinessDefinition
from business_definition_repository import PostgreSQLBusinessDefinitionRepository


def test_save_draft_to_postgresql():

    # Safety: Never run this test against our development database.
    if engine.url.database != "ai_dq_test":
        pytest.skip("Requires ai_dq_test database")

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            repo = PostgreSQLBusinessDefinitionRepository(connection)

            # 1. Create synthetic business definition
            definition = BusinessDefinition(
                definition_id="TEST_NET_REVENUE",
                version=1,
                name="Test Net Revenue",
                description="Synthetic definition for integration testing",
                formula="Payments - Refunds",
                grain="Per location per day",
                rationale="Verify PostgreSQL repository persistence",
                status="draft"
            )

            # 2. Save using our actual PostgreSQL repository
            repo.save_draft(definition)

            # 3. Read the record directly from PostgreSQL
            statement = select(BusinessDefinitionORM.status).where(
                BusinessDefinitionORM.definition_id == "TEST_NET_REVENUE",
                BusinessDefinitionORM.version == 1
            )

            saved_status = connection.execute(statement).scalar_one()

            # 4. Verify the result
            assert saved_status == "draft"

        finally:
            # 5. Remove test changes by rolling back
            transaction.rollback()


def test_get_approved_definition():

    if engine.url.database != "ai_dq_test":
        pytest.skip("Requires ai_dq_test database")

    test_definitions = [
        {
            "definition_id": "TEST_NET_REVENUE",
            "version": 1,
            "name": "Net Revenue",
            "description": "Previous synthetic definition",
            "formula": "Payments",
            "grain": "Location/day",
            "rationale": "Superseded test version",
            "status": "superseded"
        },
        {
            "definition_id": "TEST_NET_REVENUE",
            "version": 2,
            "name": "Net Revenue",
            "description": "Current synthetic approved definition",
            "formula": "Payments - Refunds",
            "grain": "Location/day",
            "rationale": "Approved test version",
            "status": "approved"
        },
        {
            "definition_id": "TEST_NET_REVENUE",
            "version": 3,
            "name": "Net Revenue",
            "description": "Proposed synthetic definition",
            "formula": "Payments - Refunds - Adjustments",
            "grain": "Location/day",
            "rationale": "Draft awaiting review",
            "status": "draft"
        }
    ]

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            # Insert all three versions
            connection.execute(
                insert(BusinessDefinitionORM),
                test_definitions
            )

            # Create repository using same connection
            repo = PostgreSQLBusinessDefinitionRepository(connection)

            # Retrieve only the approved definition
            result = repo.get_approved("TEST_NET_REVENUE")

            # Verify the correct version was retrieved
            assert result is not None
            assert result.definition_id == "TEST_NET_REVENUE"
            assert result.version == 2
            assert result.status == "approved"
            assert result.formula == "Payments - Refunds"

        finally:
            transaction.rollback()



def test_duplicate_definition_version_rejected():

    if engine.url.database != "ai_dq_test":
        pytest.skip("Requires ai_dq_test database")

    test_definition = {
        "definition_id": "TEST_DUPLICATE",
        "version": 1,
        "name": "Test Duplicate",
        "description": "Synthetic definition for testing",
        "formula": "Payments - Refunds",
        "grain": "Location/day",
        "rationale": "Test primary key constraint",
        "status": "draft"
    }

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            # First INSERT: should succeed
            connection.execute(
                insert(BusinessDefinitionORM),
                [test_definition]
            )

            # Second INSERT: same definition_id + version
            # PostgreSQL should reject the duplicate
            with pytest.raises(IntegrityError):
                connection.execute(
                    insert(BusinessDefinitionORM),
                    [test_definition]
                )

        finally:
            # Roll back the entire transaction
            transaction.rollback()

def test_only_one_approved_version_allowed():

    if engine.url.database != "ai_dq_test":
        pytest.skip("Requires ai_dq_test database")

    test_definition = [{
        "definition_id": "TEST_KPI",
        "version": 1,
        "name": "Test Partial Duplicate",
        "description": "Synthetic definition for testing",
        "formula": "Payments - Refunds",
        "grain": "Location/day",
        "rationale": "Test primary key constraint",
        "status": "approved"
    },
    {
        "definition_id": "TEST_KPI",
        "version": 2,
        "name": "Test Partial Duplicate",
        "description": "Synthetic definition for testing",
        "formula": "Payments - Refunds",
        "grain": "Location/day",
        "rationale": "Test primary key constraint",
        "status": "approved"
    }
    ]

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            # First INSERT: should succeed
            connection.execute(
                insert(BusinessDefinitionORM),
                test_definition[0]
            )

            # Second INSERT: same definition_id + version
            # PostgreSQL should reject the duplicate
            with pytest.raises(IntegrityError):
                connection.execute(
                    insert(BusinessDefinitionORM),
                    test_definition[1]
                )

        finally:
            # Roll back the entire transaction
            transaction.rollback()