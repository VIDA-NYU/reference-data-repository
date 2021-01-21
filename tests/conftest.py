# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Fixtures for unit tests."""

import pytest
import requests


INDEX_JSON = {
    'datasets': [
        {
            'id': 'DS1',
            'url': 'X',
            'format': {'type': 'csv', 'parameters': {'delim': '|'}},
            'schema': [
                {'id': 'C1'},
                {'id': 'C2', 'tags': ['x']}
            ],
            'tags': ['a']
        },
        {
            'id': 'DS2',
            'url': 'X',
            'format': {'type': 'csv', 'parameters': {}},
            'schema': [
                {'id': 'C1', 'tags': ['u', 'v']},
                {'id': 'C2', 'tags': ['w']}
            ],
            'tags': ['b']
        },
        {
            'id': 'DS3',
            'url': 'X',
            'format': {'type': 'csv', 'parameters': {}},
            'schema': [
                {'id': 'C1', 'tags': ['x']},
                {'id': 'C2', 'tags': ['y']}
            ],
            'tags': ['a', 'b']
        }
    ]
}


# -- Helper class and fixture for mocked requests -----------------------------

class MockResponse:
    """Mock response object for requests to download the repository index.
    Adopted from the online documentation at:
    https://docs.pytest.org/en/stable/monkeypatch.html
    """
    def __init__(self, *args, **kwargs):
        """Nothing to intialize. Every request will return the same object."""
        pass

    def json(self):
        """Return dictionary containing the request Url and optional data. If
        the request.
        """
        return INDEX_JSON

    def raise_for_status(self):
        """Never raise an error for a failed requests."""
        pass


@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return index document."""

    def mock_get(*args, **kwargs):
        return MockResponse(*args)

    monkeypatch.setattr(requests, "get", mock_get)
