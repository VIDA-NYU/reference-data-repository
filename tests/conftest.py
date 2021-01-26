# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Fixtures for unit tests."""

import json
import os
import pytest
import requests

import refdata.config as config


"""Path to local directory with test files."""
DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(DIR, '.files')


INDEX_JSON = {
    'datasets': [
        {
            'id': 'DS1',
            'url': 'X',
            "checksum": "0000",
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
            "checksum": "0001",
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
            "checksum": "0002",
            'format': {'type': 'csv', 'parameters': {}},
            'schema': [
                {'id': 'C1', 'tags': ['x']},
                {'id': 'C2', 'tags': ['y']}
            ],
            'tags': ['a', 'b']
        }
    ]
}


@pytest.fixture
def countries_file():
    """Get path to the `countries.json` file for tests."""
    basedir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basedir, '.files', 'countries.json')


@pytest.fixture
def index_file():
    """Get path to the default repository index file."""
    basedir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(basedir, '.files', 'index.json')


# -- Helper class and fixture for mocked requests -----------------------------

class MockResponse:
    """Mock response object for requests to download the repository index.
    Adopted from the online documentation at:
    https://docs.pytest.org/en/stable/monkeypatch.html
    """
    def __init__(self, url):
        """Keep track of the request Url to be able to load different test
        data files.
        """
        self.url = url
        self._fh = None

    def __enter__(self):
        self._fh = open(self._datafile(), 'rb')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._fh.close()

    def _datafile(self):
        """The datafile depends on the Url. It is expected that the Url
        references a file in the tests/.files folder.
        """
        return os.path.join(DATA_DIR, self.url)

    @property
    def content(self):
        """Raw response for file downloads."""
        with open(self._datafile(), 'rb') as f:
            return f.read()

    def iter_content(self, chunk_size):
        while True:
            data = self._fh.read(chunk_size)
            if not data:
                break
            yield data

    def json(self):
        """If the Url is the DEFAULT_URL the test index is returned. Otherwise
        an attempt is made to read the index data file.
        """
        if self.url == config.DEFAULT_URL:
            return INDEX_JSON
        else:
            with open(self._datafile(), 'r') as f:
                return json.load(f)

    def raise_for_status(self):
        """Never raise an error for a failed requests."""
        pass


@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return index document."""

    def mock_get(*args, **kwargs):
        return MockResponse(*args)

    monkeypatch.setattr(requests, "get", mock_get)
