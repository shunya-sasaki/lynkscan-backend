"""SoftwareCategory table models."""

from sqlmodel import Field
from sqlmodel import SQLModel


class SoftwareCategoryBase(SQLModel):
    """Base fields for SoftwareCategory."""

    name: str


class SoftwareCategory(SoftwareCategoryBase, table=True):
    """SoftwareCategory table."""

    id: int | None = Field(default=None, primary_key=True)


class SoftwareCategoryUpdate(SQLModel):
    """Partial update model for SoftwareCategory."""

    name: str | None = None
