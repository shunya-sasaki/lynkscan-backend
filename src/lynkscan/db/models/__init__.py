"""Database table models."""

from lynkscan.db.models.license import License
from lynkscan.db.models.license import LicenseUpdate
from lynkscan.db.models.license_type import LicenseType
from lynkscan.db.models.license_type import LicenseTypeUpdate
from lynkscan.db.models.software import Software
from lynkscan.db.models.software import SoftwareUpdate
from lynkscan.db.models.software_category import SoftwareCategory
from lynkscan.db.models.software_category import SoftwareCategoryUpdate
from lynkscan.db.models.software_github_evaluation import (
    SoftwareGitHubEvaluation,
)
from lynkscan.db.models.software_github_evaluation import (
    SoftwareGitHubEvaluationUpdate,
)
from lynkscan.db.models.software_vulnerability import (
    SoftwareVulnerability,
)
from lynkscan.db.models.software_vulnerability import (
    SoftwareVulnerabilityUpdate,
)
from lynkscan.db.models.usage import Usage
from lynkscan.db.models.usage import UsageUpdate
from lynkscan.db.models.vulnerability import Vulnerability
from lynkscan.db.models.vulnerability import VulnerabilityUpdate

__all__ = [
    "Software",
    "SoftwareUpdate",
    "LicenseType",
    "LicenseTypeUpdate",
    "License",
    "LicenseUpdate",
    "SoftwareCategory",
    "SoftwareCategoryUpdate",
    "SoftwareGitHubEvaluation",
    "SoftwareGitHubEvaluationUpdate",
    "Usage",
    "UsageUpdate",
    "Vulnerability",
    "VulnerabilityUpdate",
    "SoftwareVulnerability",
    "SoftwareVulnerabilityUpdate",
]
