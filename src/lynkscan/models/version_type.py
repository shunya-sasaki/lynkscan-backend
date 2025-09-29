"""Enum for version number types."""

from enum import Enum


class VersionType(str, Enum):
    """Enum for version number types."""

    SEMANTIC = "semantic"
    PREFIXED_SEMANTIC = "prefixed_semantic"
    DATE_BASED = "date_based"
    UNKNOWN = "unknown"
