from sqlalchemy import (
    Text,
    Integer,
    CheckConstraint,
    Index,
    text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
)
from sqlalchemy.engine import Engine, Connection

class Base(DeclarativeBase):
    pass


class BusinessDefinitionORM(Base):

    __tablename__ = "business_definitions"

    definition_id: Mapped[str] = mapped_column(
        Text, primary_key=True
    )

    version: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    formula: Mapped[str] = mapped_column(Text)
    grain: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Text, server_default="draft"
    )

    __table_args__ = (
        CheckConstraint(
            "version >= 1",
            name="ck_definition_version"
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'superseded')",
            name="ck_definition_status"
        ),
        Index(
            "uq_approved_definition",
            "definition_id",
            unique=True,
            postgresql_where=text("status = 'approved'")
        ),
        {"schema": "dq"}
    )