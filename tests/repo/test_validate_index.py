# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the repository index schema validator."""

from jsonschema.exceptions import ValidationError

import pytest

from refdata.repo.schema import validate


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
def test_invalid_repository_index(doc):
    """Test error for invalid repository index documents."""
    with pytest.raises(ValidationError):
        validate(doc)


@pytest.mark.parametrize(
    'doc',
    [
        {
            'datasets': [
                {
                    'id': '0000',
                    'url': 'xyz.com',
                    'checksum': '0',
                    'schema': [{'id': 'C1'}],
                    'format': {'type': 'csv', 'parameters': {}}
                }
            ]
        },
        {
            'datasets': [
                {
                    'id': '0000',
                    'url': 'xyz.com',
                    'checksum': '0',
                    'schema': [{'id': 'C1'}],
                    'format': {'type': 'csv', 'parameters': {}}
                }
            ],
            'repositories': ['abc.org']
        }
    ]
)
def test_valid_repository_index(doc):
    """Test correct validation for valid repository index documents."""
    validate(doc)
