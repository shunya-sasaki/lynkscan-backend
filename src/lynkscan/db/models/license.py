"""License table models."""

from sqlmodel import Field
from sqlmodel import SQLModel


class LicenseBase(SQLModel):
    """Base fields for License."""

    name: str
    identifier: str = Field(description="SPDX identifier")
    is_fsf_free: bool = Field(description="Is FSF free software license")
    is_osi_approved: bool = Field(description="Is OSI approved license")
    category_id: int = Field(foreign_key="license_category.id")


class License(LicenseBase, table=True):
    """License table."""

    id: int | None = Field(default=None, primary_key=True)


class LicenseUpdate(SQLModel):
    """Partial update model for License."""

    name: str
    identifier: str
    is_fsf_free: bool = Field(description="Is FSF free software license")
    is_osi_approved: bool = Field(description="Is OSI approved license")
    category_id: int = Field(foreign_key="license_category.id")
