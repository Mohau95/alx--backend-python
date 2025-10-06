#!/usr/bin/env python3
"""Unit and integration tests for client.GithubOrgClient."""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock
import client
import utils

class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([("google",), ("abc",)])
    @patch('utils.get_json')
    def test_org(self, org_name, mock_get_json):
        mock_get_json.return_value = {"login": org_name}
        g = client.GithubOrgClient(org_name)
        self.assertEqual(g.org(), {"login": org_name})
        mock_get_json.assert_called_once()

    def test_public_repos_url(self):
        payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        with patch.object(client.GithubOrgClient, 'org', return_value=payload):
            g = client.GithubOrgClient('test')
            self.assertEqual(g._public_repos_url, payload['repos_url'])

    @patch('utils.get_json')
    def test_public_repos(self, mock_get_json):
        sample_repos = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = sample_repos
        with patch.object(client.GithubOrgClient, '_public_repos_url', new_callable=Mock) as mock_url:
            mock_url.return_value = 'https://api.github.com/orgs/test/repos'
            g = client.GithubOrgClient('test')
            repos = g.public_repos()
            self.assertEqual(repos, [r['name'] for r in sample_repos])
            mock_url.assert_called()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        g = client.GithubOrgClient('test')
        self.assertEqual(g.has_license(repo, license_key), expected)

@parameterized_class(('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'), [(None, None, None, None)])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fixtures import org_payload, repos_payload, expected_repos, apache2_repos
        cls.org_payload = org_payload
        cls.repos_payload = repos_payload
        cls.expected_repos = expected_repos
        cls.apache2_repos = apache2_repos
        cls.get_patcher = patch('requests.get')
        mock_get = cls.get_patcher.start()
        def _mock_get(url):
            mock_resp = Mock()
            if url.endswith('/repos'):
                mock_resp.json.return_value = cls.repos_payload
            else:
                mock_resp.json.return_value = cls.org_payload
            return mock_resp
        mock_get.side_effect = _mock_get

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        g = client.GithubOrgClient('test')
        repos = g.public_repos()
        self.assertEqual(repos, self.expected_repos)
        apache2 = g.public_repos(license_key='apache-2.0')
        self.assertEqual(apache2, self.apache2_repos)
