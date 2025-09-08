"""Software table model."""

from sqlmodel import Field
from sqlmodel import SQLModel


class SoftwareBase(SQLModel):
    """Base class for Software table model."""

    name: str
    identifier: str
    latest_version: str
    official_site_url: str
    repo_url: str
    category_id: int = Field(foreign_key="software_category.id")
    license_id: int = Field(foreign_key="license.id")


class Software(SoftwareBase, table=True):
    """Software table model."""

    id: int | None = Field(default=None, primary_key=True)


class SoftwareUpdate(SQLModel):
    """Software update model."""

    name: str | None = None
    identifier: str | None = None
    latest_version: str | None = None
    official_site_url: str | None = None
    repo_url: str | None = None
    category_id: int | None = Field(
        default=None, foreign_key="software_category.id"
    )
    # Correct foreign key points to license.id (typo was "licese")
    license_id: int | None = Field(default=None, foreign_key="license.id")
