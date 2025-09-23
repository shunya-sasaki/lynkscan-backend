"""GitHub repo scanner."""

import base64
import json
import os
from typing import Literal

import requests
from packaging.version import InvalidVersion
from packaging.version import Version


class GitHubRepoVulnerability:
    """GitHub repository vulnerability information."""

    def __init__(
        self,
        ghsa_id: str | None,
        cve_id: str | None,
        affected_version_ranges: str,
    ):
        """Initialize GitHubRepoVulnerability."""
        self.ghsa_id = ghsa_id
        self.cve_id = cve_id
        self.affected_version_ranges = affected_version_ranges
        self.affected_tags: list[str] = []

    def evaluate_tags(self, tags: list[str]) -> list[str]:
        """Evaluate if the given tags are affected by the vulnerability."""
        target_tags = [tag for tag in tags if self._is_semantic_version(tag)]
        semantic_tags = [tag.lstrip("v") for tag in target_tags]
        for vuln_range in self.affected_version_ranges:
            version_range_strs = vuln_range.split(",")
            is_ge = [True] * len(semantic_tags)
            is_le = [True] * len(semantic_tags)
            for version_str in version_range_strs:
                if ">=" in version_str:
                    init_version = version_str.replace(">=", "").strip()
                    is_ge = [
                        Version(init_version) <= Version(tag)
                        for tag in semantic_tags
                    ]
                elif ">" in version_str:
                    init_version = version_str.replace(">", "").strip()
                    is_ge = [
                        Version(init_version) < Version(tag)
                        for tag in semantic_tags
                    ]
                if "<=" in version_str:
                    last_version = version_str.replace("<=", "").strip()
                    is_le = [
                        Version(last_version) >= Version(tag)
                        for tag in semantic_tags
                    ]
                elif "<" in version_str:
                    end_version = version_str.replace("<", "").strip()
                    is_le = [
                        Version(end_version) > Version(tag)
                        for tag in semantic_tags
                    ]
            is_affected = [ge and le for ge, le in zip(is_ge, is_le)]
            affected_tags = [
                tag
                for tag, affected in zip(target_tags, is_affected)
                if affected
            ]
        self.affected_tags = affected_tags
        return affected_tags

    def _is_semantic_version(self, tag: str) -> bool:
        trimed_tag = tag.lstrip("v")
        try:
            Version(trimed_tag)
            return True
        except Exception:
            return False


class GitHubRelease:
    """GitHub release data."""

    def __init__(
        self,
        identifier: str,
        tag: str,
        clone_url: str,
    ):
        """Initialize GitHubRelease."""
        self.identifier = identifier
        self.tag = tag
        self.clone_url = clone_url
        self.vulnerabilities: list[GitHubRepoVulnerability] = []

    def add_vulns(self, vulns: list[GitHubRepoVulnerability]):
        """Add vulnerability info to the release."""
        for vuln in vulns:
            if self.tag in vuln.affected_tags:
                self.vulnerabilities.append(vuln)

    def fetch_vulns_from_osv(self):
        """Fetch vulnerability info for the release from OSV database."""
        payload = {
            "package": {"name": self.clone_url, "ecosystem": "GIT"},
            "version": self.tag,
        }
        url = "https://api.osv.dev/v1/query"
        response = requests.post(url, json=payload)
        data = response.json()
        if data:
            for vuln in data["vulns"]:
                cve_codes = vuln["id"]
                self.vulnerabilities.extend(cve_codes)


class GitHubRepo:
    """GitHub repository meta information."""

    def __init__(self, owner: str, repo: str):
        """Initialize GitHubRepo."""
        self.owner = owner
        self.repo = repo
        self.identifier = f"{owner}/{repo}"
        self.description = ""
        self.stars = 0
        self.forks = 0
        self.license: str | None = None
        self.tags: list[str] = []
        self.previous_releases: list[GitHubRelease] = []
        self.is_verified: bool = False
        self.has_sponsors: bool = False
        self.homepage: str = ""
        self.repo_url: str = ""
        self.clone_url: str = ""
        self.latest_version: str = ""
        self.owner_type: Literal["User", "Organization"] = "User"
        self._headers = self._check_auth()

    def _check_auth(self) -> dict[str, str]:
        """Check for GitHub authentication token from environment variable."""
        headers = {}
        token = os.getenv("GITHUB_TOKEN")
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        return headers

    def _detect_latest_version(self, tags: list[str]) -> str:
        """Detect the latest version from the list of tags."""
        semantic_tags = [tag for tag in tags if self._is_semantic_version(tag)]
        if not semantic_tags:
            return "N/A"
        semantic_tags = sorted(
            semantic_tags,
            key=lambda tag: Version(tag.lstrip("v")),
            reverse=True,
        )
        return semantic_tags[0]

    def _is_semantic_version(self, tag: str) -> bool:
        trimed_tag = tag.lstrip("v")
        try:
            Version(trimed_tag)
            return True
        except Exception:
            return False

    def fetch_infos(self, with_file: bool = False):
        """Fetch meta info, tags, and vulnerabilities from GitHub API."""
        self.fetch_repoinfo(with_file=with_file)
        releases = self.fetch_releases(with_file=with_file)
        vulnerabilities = self.fetch_vulnerabilities(with_file=with_file)
        release_tags = [release.tag for release in releases]
        self.latest_version = self._detect_latest_version(release_tags)
        if self.owner_type == "Organization":
            self.fetch_owner_verification()
        for vuln in vulnerabilities:
            _ = vuln.evaluate_tags(tags=release_tags)
        for release in releases:
            release.add_vulns(vulnerabilities)

    def fetch_repoinfo(self, with_file: bool = False):
        """Fetch repo information from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}",
            headers=self._headers,
        )
        data = response.json()
        if with_file:
            with open(f"github-repoinfo-{self.repo}.json", "w") as fout:
                json.dump(data, fout, indent=2)
        self.description = data.get("description", "")
        self.forks = data.get("forks", 0)
        self.stars = data.get("stargazers_count", 0)
        self.license = data.get("license", {}).get("spdx_id", None)
        self.homepage = data.get("homepage", "")
        self.repo_url = data.get("html_url", "")
        self.clone_url = data.get("clone_url", "")
        self.owner_type = data.get("owner", {}).get("type", "User")

    def fetch_tags(self, with_file: bool = False) -> list[str]:
        """Fetch repo tags from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/tags",
            headers=self._headers,
        )
        data = response.json()
        if with_file:
            with open(f"github-repotags-{self.repo}.json", "w") as fout:
                json.dump(data, fout, indent=2)
        tags = [tag["name"] for tag in data]
        return tags

    def fetch_vulnerabilities(
        self, with_file: bool = False
    ) -> list[GitHubRepoVulnerability]:
        """Fetch vulnerabilities of the repo from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/security-advisories",
            headers=self._headers,
        )
        data = response.json()
        if with_file:
            with open(
                f"github-repo-vulnerabilities-{self.repo}.json", "w"
            ) as fout:
                json.dump(data, fout, indent=2)
        vulns: list[GitHubRepoVulnerability] = []
        for item in data:
            ghsa_id = item.get("ghsa_id", None)
            cve_id = item.get("cve_id", None)
            vulnerabilities = item.get("vulnerabilities", [])
            str_version_ranges: list[str] = []
            for vuln in vulnerabilities:
                str_version_range = vuln.get("vulnerable_version_range", "")
                str_version_ranges.append(str_version_range)
            vulnerability = GitHubRepoVulnerability(
                ghsa_id=ghsa_id,
                cve_id=cve_id,
                affected_version_ranges=str_version_ranges,
            )
            vulns.append(vulnerability)
        return vulns

    def fetch_releases(self, with_file: bool = False) -> list[GitHubRelease]:
        """Fetch repo releases from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/releases",
            headers=self._headers,
        )
        releases = response.json()
        if with_file:
            with open(f"github-reporeleases-{self.repo}.json", "w") as fout:
                json.dump(releases, fout, indent=2)
        release_tags = [
            release["tag_name"]
            for release in releases
            if release["prerelease"] is False
        ]
        previous_releases = [
            GitHubRelease(
                identifier=self.identifier, tag=tag, clone_url=self.clone_url
            )
            for tag in release_tags
        ]
        previous_releases = sorted(
            previous_releases, key=self._version_key, reverse=True
        )
        self.previous_releases = previous_releases
        return previous_releases

    def fetch_license_text(self) -> str:
        """Fetch license file from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/license",
            headers=self._headers,
        )
        data_license = response.json()
        content = data_license["content"]
        content_str = base64.b64decode(content).decode("utf-8")
        return content_str

    def fetch_owner_verification(self) -> bool:
        """Fetch owner verification status from GitHub API."""
        response = requests.get(
            f"https://api.github.com/orgs/{self.owner}",
            headers=self._headers,
        )
        data = response.json()
        is_verified = data.get("is_verified", False)
        self.is_verified = is_verified
        return is_verified

    def _version_key(self, release: GitHubRelease):
        tag = release.tag.lstrip("v")
        try:
            return (0, Version(tag))
        except InvalidVersion:
            return (1, tag)
