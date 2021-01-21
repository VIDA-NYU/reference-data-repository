# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the dataset repository."""

from jsonschema.exceptions import ValidationError

import pytest
from refdata.repo import RepositoryManager, validate


def test_get_dataset(mock_response):
    """Test getting a dataset from the test repository."""
    repo = RepositoryManager()
    assert repo.get('DS1').identifier == 'DS1'
    assert repo.get('UNKNOWN') is None


@pytest.mark.parametrize(
    'doc',
    [
        {'datasets': [{'name': 'ABC'}]},
        {
            'datasets': [
                {
                    'id': 'DS1',
                    'url': 'X',
                    'format': {'type': 'csv', 'parameters': []},
                    'schema': [
                        {'id': 'C1'},
                        {'id': 'C2', 'tags': ['x']}
                    ],
                    'tags': ['a']
                }
            ]
        },
        {
            'datasets': [
                {
                    'id': 'DS1',
                    'url': 'X',
                    'format': {'type': 'undefined', 'parameters': {}},
                    'schema': [
                        {'id': 'C1'},
                        {'id': 'C2', 'tags': ['x']}
                    ],
                    'tags': ['a']
                }
            ]
        }
    ]
)
def test_invalid_repository_index(doc, mock_response):
    """Test error for invalid repository index documents."""
    with pytest.raises(ValidationError):
        validate(doc)


def test_valid_repository_index(mock_response):
    """Test validating a 'downloaded' repository index document."""
    validate('just.a.string')
