"""NPM package scanner.

Examples:
    >>> package = PythonPackage("requests")
    >>> package.fetch_meta_info()
    >>> for release in package.releases:
    >>>     print(f"{release.version}: {release.upload_time}")
"""

import json
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import requests


class NpmRelease:
    """NPM previous release data."""

    def __init__(self, name: str, version: str, upload_time: datetime):
        """Initialize NpmReleaseData."""
        self.name = name
        self.version = version
        self.upload_time = upload_time
        self.vulnerabilities: list[str] = []

    def fetch_vulns_from_osv(self):
        """Fetch vulnerability info for the release from OSV database."""
        payload = {
            "package": {"name": self.name, "ecosystem": "npm"},
            "version": self.version,
        }
        url = "https://api.osv.dev/v1/query"
        reponse = requests.post(url, json=payload)
        data = reponse.json()
        if data:
            for vuln in data["vulns"]:
                cve_codes = vuln["id"]
                self.vulnerabilities.extend(cve_codes)

    class NpmPackage:
        """NPM pacakge meta information."""

        def __init__(self, name: str, years_back: int = 5):
            """Initialize NpmPackage."""
            self.name = name
            self.description = ""
            self.latest_version = ""
            self.license = ""
            self.previous_releases: list[NpmRelease] = []
            self.years_back = years_back
            self.since = self._determine_since()

        def _determine_since(self) -> datetime:
            """Determine the datetime since when to fetch previous releases."""
            now = datetime.now(timezone.utc)
            since = now - timedelta(days=365 * self.years_back)
            return since

        def fetch_meta_info(self):
            """Fetch meta information for the package from NPM registry."""
            url = f"https://registry.npmjs.org/{self.name}/latest"
            response = requests.get(url)
            data = response.json()
            with open(f"npm-{self.name.replace('/', '-')}") as fout:
                json.dump(data, fout, indent=2)
            self.description = data.get("description", "")
            self.latest_version = data.get("version", "unknown")
            self.license = data.get("license", "unknown")

            full_response = requests.get(
                f"https://registry.npmjs.org/{self.name}"
            )
            full_data = full_response.json()
            with open(
                f"npm-{self.name.replace('/', '-')}-full.json", "w"
            ) as fout:
                json.dump(full_data, fout, indent=2)
            self.upload_times = datetime.fromisoformat(
                full_data["time"]["modified"]
            )
            for version, upload_time_str in full_data["time"].items():
                if self.is_stable_version(version):
                    upload_time = datetime.fromisoformat(upload_time_str)
                    if upload_time < self.since:
                        continue
                    release = NpmRelease(self.name, version, upload_time)
                    release.fetch_vulns_from_osv()
                    self.previous_releases.append(release)

        def is_stable_version(self, version: str) -> bool:
            """Check if the version is a stable release."""
            return not re.search(r"[a-zA-Z]", version)
