"""Utility to detect version number types."""

from __future__ import annotations

import re

from packaging.version import Version

from lynkscan.models.version_type import VersionType


class VersionDetector:
    """Utility class for detecting version number types."""

    @staticmethod
    def detect_version_type(version_str: str) -> VersionType:
        """Detect the type of version number."""
        if re.match(r"^\d+\.\d[\.\d]*$", version_str):
            return VersionType.SEMANTIC
        if re.match(r"^v\d+\.\d[\.\d]*$", version_str):
            return VersionType.PREFIXED_SEMANTIC
        if re.match(r"\d{8}-\d{6}-[a-f0-9]+", version_str):
            return VersionType.DATE_BASED
        return VersionType.UNKNOWN

    @classmethod
    def detect_verion_type_from_list(cls, tags: list[str]) -> VersionType:
        """Detect version types from a list of version strings."""
        semantic_tags = []
        prefixed_semantic_tags = []
        datebased_tags = []
        unknown_tags = []
        for tag in tags:
            version_type = cls.detect_version_type(tag)
            match version_type:
                case VersionDetector.VersionType.SEMANTIC:
                    semantic_tags.append(tag)
                case VersionDetector.VersionType.PREFIXED_SEMANTIC:
                    prefixed_semantic_tags.append(tag)
                case VersionDetector.VersionType.DATE_BASED:
                    datebased_tags.append(tag)
                case VersionDetector.VersionType.UNKNOWN:
                    unknown_tags.append(tag)
        if len(semantic_tags) > 0:
            return VersionType.SEMANTIC
        elif len(prefixed_semantic_tags) > 0:
            return VersionType.PREFIXED_SEMANTIC
        elif len(datebased_tags) > 0:
            return VersionType.DATE_BASED
        else:
            return VersionType.UNKNOWN

    @classmethod
    def extract_specific_type_versions(
        cls, tags: list[str], version_type: VersionType
    ) -> list[str]:
        """Extract versions of a specific type from a list of version strings.

        Args:
            tags (list[str]): List of version strings.
            version_type (VersionType): The version type to filter by.
        """
        return [
            tag for tag in tags if cls.detect_version_type(tag) == version_type
        ]

    @classmethod
    def match_to_condition(cls, version_str: str, condition_str: str) -> bool:
        """Convert a version match string to a condition string.

        Args:
            version_str (str): The version string to match.
                e.g., "v1.2.3", "1.2.3".
            condition_str (str): The condition string to convert.
                e.g., "<= v1.2.3", ">= 1.2.3", "v1.2.3", "v1.2.3 and prior",
                "v1.2.3-v1.2.5".
        """
        ge_version = None
        le_version = None
        gt_version = None
        lt_version = None
        if "<=" in condition_str:
            le_version = condition_str.split("<=")[1].strip()
        elif ">=" in condition_str:
            ge_version = condition_str.split(">=")[1].strip()
        elif ">" in condition_str:
            gt_version = condition_str.split(">")[1].strip()
        elif "<" in condition_str:
            lt_version = condition_str.split("<")[1].strip()
        elif "and prior" in condition_str:
            le_version = condition_str.split(" and prior")[0].strip()
        elif match := re.match(
            r"[a-zA-Z0-9\.]*-[a-zA-Z0-9\.]*", condition_str
        ):
            versions = match.group(0).split("-")
            ge_version = versions[0].strip()
            le_version = versions[1].strip()
        else:
            le_version = condition_str.strip()
            ge_version = le_version
        result = cls._compare_versions(
            target_version=version_str,
            ge_version=ge_version,
            le_version=le_version,
            gt_version=gt_version,
            lt_version=lt_version,
        )
        return result

    @staticmethod
    def _compare_versions(
        target_version: str,
        ge_version: str | None = None,
        le_version: str | None = None,
        gt_version: str | None = None,
        lt_version: str | None = None,
    ) -> bool:
        """Compare a target version against specified version constraints.

        Args:
            target_version (str): The version string to compare.
            ge_version (str | None): The version string for "greater than or equal to" comparison.
            le_version (str | None): The version string for "less than or equal to" comparison.
            gt_version (str | None): The version string for "greater than" comparison.
            lt_version (str | None): The version string for "less than" comparison.

        Returns:
            bool: True if the target version satisfies all specified constraints, False otherwise.
        """
        result = True
        version_type = VersionDetector.detect_version_type(target_version)
        if version_type in [
            VersionType.SEMANTIC,
            VersionType.PREFIXED_SEMANTIC,
        ]:
            if ge_version is not None:
                result = result and Version(target_version) >= Version(
                    ge_version
                )
            if le_version is not None:
                result = result and Version(target_version) <= Version(
                    le_version
                )
            if gt_version is not None:
                result = result and Version(target_version) > Version(
                    gt_version
                )
            if lt_version is not None:
                result = result and Version(target_version) < Version(
                    lt_version
                )
        else:
            if ge_version is not None:
                result = result and target_version >= ge_version
            if le_version is not None:
                result = result and target_version <= le_version
            if gt_version is not None:
                result = result and target_version > gt_version
            if lt_version is not None:
                result = result and target_version < lt_version
        return result
