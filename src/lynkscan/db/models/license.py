"""License table models."""

from sqlmodel import Field
from sqlmodel import SQLModel


class LicenseBase(SQLModel):
    """Base fields for License."""

    name: str
    type_id: int = Field(foreign_key="license_type.id")


class License(LicenseBase, table=True):
    """License table."""

    id: int | None = Field(default=None, primary_key=True)


class LicenseUpdate(SQLModel):
    """Partial update model for License."""

    name: str | None = None
    type_id: int | None = Field(default=None, foreign_key="license_type.id")
