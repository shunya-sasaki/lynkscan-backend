"""License information model."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from lynkscan.models.license_category import LicenseCategory
from lynkscan.utils import FormatConverter


class LicenseInfo(BaseModel):
    """LicenseInfo data model."""

    model_config = ConfigDict(
        alias_generator=FormatConverter.snake_to_camel,
        populate_by_name=True,
        use_enum_values=True,
    )

    full_name: str = Field(
        description="Full name of the license, e.g.,"
        + " 'Apache License 2.0', 'MIT License'."
    )
    identifier: str = Field(
        description="SPDX identifier of the license, e.g., 'Apache-2.0'"
    )
    is_fsf_free: bool = Field(
        description="Whether the license is Free Software"
        + " as defined by the Free Software Foundation (FSF)."
    )
    is_osi_approved: bool = Field(
        description="Whether the license is approved by"
        + " the Open Source Initiative (OSI)."
    )
    category: LicenseCategory = Field(
        description="Category of the license, e.g.,"
        + " 'Copyleft', 'Weak Copyleft', 'Permissive', 'Non permissive'."
    )
