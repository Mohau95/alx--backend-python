#!/usr/bin/env python3
"""Utilities module for JSON, nested map access, and memoization."""
import requests
from typing import Mapping, Sequence, Any
from functools import wraps

def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access a nested map with a sequence of keys."""
    for key in path:
        nested_map = nested_map[key]
    return nested_map

def get_json(url: str) -> dict:
    """Get JSON data from a URL."""
    response = requests.get(url)
    return response.json()

def memoize(fn):
    """Decorator to cache the output of a method."""
    attr_name = "_{}".format(fn.__name__)
    @wraps(fn)
    def memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return property(memoized)
