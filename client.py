#!/usr/bin/env python3
"""Client module for interacting with GitHub organizations."""
import requests
from utils import get_json, memoize

class GithubOrgClient:
    """GitHub organization client."""
    def __init__(self, org_name):
        self._org_name = org_name

    @memoize
    def org(self):
        """Return the organization information."""
        url = f"https://api.github.com/orgs/{self._org_name}"
        return get_json(url)

    @property
    def _public_repos_url(self):
        """Return the URL for the public repositories."""
        return self.org.get("repos_url")

    def public_repos(self, license_key=None):
        """Return the list of public repositories."""
        repos = get_json(self._public_repos_url)
        repo_names = [repo["name"] for repo in repos]
        if license_key is None:
            return repo_names
        return [repo["name"] for repo in repos if self.has_license(repo, license_key)]

    @staticmethod
    def has_license(repo, license_key):
        """Check if repo has a specific license."""
        try:
            return repo["license"]["key"] == license_key
        except (KeyError, TypeError):
            return False
