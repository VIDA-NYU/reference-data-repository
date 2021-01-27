# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the dataset handle."""

import pytest

from refdata.store.dataset import DatasetHandle

import refdata.error as err


def test_format_error():
    """Ensure that the proper error is raised when initializing a dataset
    handle with an invalid format identifier.
    """
    doc = {
        'id': '0000',
        'url': 'countries.json',
        "checksum": "889c264f2ac4629b4998aa8b8b1d4de45890c39c10e24cfd8a017e9924e805c7",
        "schema": [{"id": "name"}, {"id": "alpha2Code"}],
        "format": {
            "type": "unknown",
            "parameters": {}
        }
    }
    with pytest.raises(err.InvalidFormatError):
        DatasetHandle(doc=doc, datafile='/dev/null')


def test_load_distinct(store):
    """Test downloading the U.S. cities test dataset and getting a list of
    distinct state names via the local data store.
    """
    values = store.distinct(key='cities', columns='state', auto_download=True)
    assert len(values) == 1
    assert 'Alabama' in values
    values = store.distinct(key='cities', auto_download=False)
    assert len(values) == 7


def test_load_data_frame(store):
    """Test downloading and loading the U.S. cities test dataset via the local
    data store.
    """
    df = store.load(key='cities', auto_download=True)
    assert df.shape == (7, 2)
    assert list(df.columns) == ['city', 'state']
    df = store.load(key='cities', columns=['city'])
    assert df.shape == (7, 1)
    assert list(df.columns) == ['city']


def test_load_mapping(store):
    """Test downloading the U.S. cities test dataset and getting a mapping of
    values for columns from the downloaded dataset.
    """
    mapping = store.mapping(key='cities', lhs='city', rhs='state', auto_download=True)
    assert len(mapping) == 7
    assert mapping['Troy'] == 'Alabama'
    values = store.mapping(key='cities', lhs='city', rhs=['city'])
    assert len(values) == 0
    values = store.mapping(key='cities', lhs='city', rhs=['city'], ignore_equal=False)
    assert len(values) == 7
