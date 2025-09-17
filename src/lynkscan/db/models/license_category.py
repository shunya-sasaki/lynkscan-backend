"""LicenseCategory table models (formerly LicenseType)."""

from sqlmodel import Field
from sqlmodel import SQLModel


class LicenseCategoryBase(SQLModel):
    """Base fields for LicenseCategory."""

    type: str


class LicenseCategory(LicenseCategoryBase, table=True):
    """License category table (e.g., Permissive, Copyleft)."""

    __tablename__ = "license_category"

    id: int | None = Field(default=None, primary_key=True)


class LicenseCategoryUpdate(SQLModel):
    """Partial update model for LicenseCategory."""

    type: str | None = None
