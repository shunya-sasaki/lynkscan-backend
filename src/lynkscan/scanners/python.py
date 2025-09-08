"""PyPI package scanner.

Examples:
    >>> package = PythonPackage("requests")
    >>> package.fetch_meta_info()
    >>> for release in package.releases:
    >>>     print(f"{release.version}: {release.upload_time}")
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TypedDict

import requests


class PythonPackageData(TypedDict):
    """Python package data from PyPI API JSON."""

    info: dict
    last_serial: int
    releases: dict[str, list]
    urls: list[dict]
    vulnerabilities: list


class PythonRelease:
    """Python previous release data."""

    def __init__(self, name: str, version: str, upload_time: datetime):
        """Initialize PythonReleaseData."""
        self.name = name
        self.version = version
        self.upload_time = upload_time
        self.vulnerabilities: list[str] = []

    def fetch_meta_info(self) -> None:
        """Fetch meta information for the release from PyPI repo."""
        url = f"https://pypi.org/pypi/{self.name}/{self.version}/json"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return
        data: PythonPackageData = response.json()
        for vuln in data.get("vulnerabilities", []):
            cve_codes = vuln["alias"]
            self.vulnerabilities.extend(cve_codes)


class PythonPackage:
    """Python pacakge meta information."""

    def __init__(self, name: str, years_back: int = 5):
        """Initialize PythonPackage."""
        self.name = name
        self.description = ""
        self.latest_version = ""
        self.license = ""
        self.previous_releases: list[PythonRelease] = []
        self.vulnerabilities: list[str] = []
        self.since = self._datetime_since(years_back)

    def _datetime_since(self, years_back: int = 5):
        """Get datetime object for years back."""
        return datetime.now(timezone.utc) - timedelta(days=years_back * 365)

    def fetch_meta_info(self):
        """Fetch package meta info from PyPI."""
        url = f"https://pypi.org/pypi/{self.name}/json"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        data: PythonPackageData = response.json()
        info = data.get("info", None)
        if info is not None:
            self.description = info.get("summary", "")
            self.latest_version = info.get("version", "")
            classifires = info.get("classifiers", [])
            for classifier in classifires:
                if classifier.startswith("License"):
                    self.license = classifier.split("::")[-1].strip()
                    break
        for version, release_info in data.get("releases", {}).items():
            if len(release_info) == 0:
                continue
            upload_time = datetime.fromisoformat(
                release_info[-1]["upload_time"]
            )
            if upload_time >= self.since:
                release = PythonRelease(self.name, version, upload_time)
                release.fetch_meta_info()
                self.previous_releases.append(release)
        for vuln in data["vulnerabilities"]:
            cve_codes = vuln["aliases"]
            self.vulnerabilities.extend(cve_codes)
