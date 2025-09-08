"""Database table models."""

from lynkscan.db.models.license import License
from lynkscan.db.models.license import LicenseUpdate
from lynkscan.db.models.license_type import LicenseType
from lynkscan.db.models.license_type import LicenseTypeUpdate
from lynkscan.db.models.software import Software
from lynkscan.db.models.software import SoftwareUpdate

__all__ = [
    "Software",
    "SoftwareUpdate",
    "LicenseType",
    "LicenseTypeUpdate",
    "License",
    "LicenseUpdate",
]
