#!/usr/bin/env python3
"""Unit tests for utils module."""
import unittest
from parameterized import parameterized
from unittest.mock import Mock, patch
import utils

class TestAccessNestedMap(unittest.TestCase):
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        self.assertEqual(utils.access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, missing):
        with self.assertRaises(KeyError) as cm:
            utils.access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{missing}'")

class TestGetJson(unittest.TestCase):
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        mock_resp = Mock()
        mock_resp.json.return_value = test_payload
        with patch('requests.get', return_value=mock_resp) as mock_get:
            result = utils.get_json(test_url)
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)

class TestMemoize(unittest.TestCase):
    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42

            @utils.memoize
            def a_property(self):
                return self.a_method()
        tc = TestClass()
        with patch.object(TestClass, 'a_method', return_value=42) as mocked:
            first = tc.a_property
            second = tc.a_property
            self.assertEqual(first, 42)
            self.assertEqual(second, 42)
            mocked.assert_called_once()
