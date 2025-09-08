"""GitHub repo scanner."""

import json

import requests


class GitHubRepo:
    """GitHub repository meta information."""

    def __init__(self, owner: str, repo: str):
        """Initialize GitHubRepo."""
        self.owner = owner
        self.repo = repo
        self.description = ""
        self.stars = 0
        self.forks = 0
        self.license = None

    def fetch_repoinfo(self):
        """Fetch repo information from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repose/{self.owner}/{self.repo}"
        )
        data = response.json()
        with open(f"github-repoinfo-{self.repo}.json", "w") as fout:
            json.dump(data, fout, indent=2)

    def fetch_tags(self):
        """Fetch repo tags from GitHub API."""
        response = requests.get(
            f"https://api.github.com/repose/{self.owner}/{self.repo}/tags"
        )
        data = response.json()
        with open(f"github-repotags-{self.repo}.json", "w") as fout:
            json.dump(data, fout, indent=2)
