"""Vulnerability severity levels."""

from enum import Enum


class VulnerabilitySeverity(str, Enum):
    """Enumeration of vulnerability severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
