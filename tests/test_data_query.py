# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for querying dataset descriptors."""

import pytest

from refdata.base import DatasetDescriptor
from refdata.repo import RepositoryManager


"""Dataset for single dataset match tests."""
DS = DatasetDescriptor({
    'id': '0000',
    'url': 'mydata.download',
    'format': {
        'type': 'csv',
        'parameters': {}
    },
    'schema': [
        {'id': 'C1', 'tags': ['x']},
        {'id': 'C2', 'tags': ['x', 'y']}
    ],
    'tags': ['a', 'b']
})


@pytest.mark.parametrize(
    'query,result',
    [
        (set(), True),
        ({'a'}, True),
        ({'b'}, True),
        ({'x'}, True),
        ({'y'}, True),
        ({'a', 'b'}, True),
        ({'a', 'b', 'x'}, True),
        ({'a', 'b', 'y'}, True),
        ({'a', 'b', 'x', 'y'}, True),
        ({'e'}, False),
        ({'a', 'e'}, False),
        ({'a', 'b', 'x', 'z'}, False),
        ({'a', 'b', 'x', 'y', 'z'}, False)
    ]
)
def test_dataset_query(query, result):
    """Test matching dataset object tags to a given query set."""
    assert DS.matches(query=query) == result


@pytest.mark.parametrize(
    'query,result',
    [
        (None, ['DS1', 'DS2', 'DS3']),
        ('a', ['DS1', 'DS3']),
        ({'b'}, ['DS2', 'DS3']),
        (['a', 'b'], ['DS3']),
        (['a', 'b', 'c'], []),
        ({'a', 'x'}, ['DS1', 'DS3']),
        ({'a', 'x', 'y'}, ['DS3'])
    ]
)
def test_repository_query(query, result, mock_response):
    """Test querying the text repository."""
    repo = RepositoryManager()
    datasets = [ds.identifier for ds in repo.find(filter=query)]
    assert datasets == result
