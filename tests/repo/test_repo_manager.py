# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the dataset repository."""

from refdata.repo.loader import UrlLoader
from refdata.repo.manager import RepositoryManager


def test_get_dataset(mock_response):
    """Test getting a dataset from the default repository."""
    # Will attempt to download the default repository. The mocked response will
    # return the content of the `index.json` file in the test files directory.
    repo = RepositoryManager(doc=UrlLoader().load())
    assert repo.get(key='DS1').identifier == 'DS1'
    assert repo.get(key='UNKNOWN') is None


def test_read_linked_index(mock_response):
    """Test reading a federated repository index."""
    repo = RepositoryManager(doc=UrlLoader(url='multi-index.json').load())
    assert len(repo.find()) == 3
    assert repo.get('us_cities') is not None
    assert repo.get('cities') is not None
