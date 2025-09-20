"""License categories."""

from enum import Enum


class LicenseCategory(str, Enum):
    """License categories."""

    COPYLEFT: str = "Copyleft"
    WEAK_COPYLEFT: str = "Weak Copyleft"
    PERMISSIVE: str = "Permissive"
    NON_PERMISSIVE: str = "Non Permissive"
