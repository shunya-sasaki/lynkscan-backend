"""LicenseType table models."""

from sqlmodel import Field
from sqlmodel import SQLModel


class LicenseTypeBase(SQLModel):
    """Base fields for LicenseType."""

    type: str


class LicenseType(LicenseTypeBase, table=True):
    """License type table (e.g., Permissive, Copyleft)."""

    id: int | None = Field(default=None, primary_key=True)


class LicenseTypeUpdate(SQLModel):
    """Partial update model for LicenseType."""

    type: str | None = None
