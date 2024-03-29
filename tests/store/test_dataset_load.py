# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for creating different data objects for downloaded datasets."""


def test_load_distinct(store):
    """Test downloading the U.S. cities test dataset and getting a list of
    distinct state names via the local data store.
    """
    values = store.load(key='cities', auto_download=True).distinct(columns='state')
    assert len(values) == 1
    assert 'Alabama' in values
    values = store.load(key='cities').distinct(columns='state', transformer=str.lower)
    assert len(values) == 1
    assert 'alabama' in values
    values = store.load(key='cities').distinct()
    assert len(values) == 7


def test_load_data_frame(store):
    """Test downloading and loading the U.S. cities test dataset via the local
    data store.
    """
    df = store.load(key='cities', auto_download=True).df()
    assert df.shape == (7, 2)
    assert list(df.columns) == ['city', 'state']
    df = store.load(key='cities').df(columns=['city'])
    assert df.shape == (7, 1)
    assert list(df.columns) == ['city']


def test_load_mapping(store):
    """Test downloading the U.S. cities test dataset and getting a mapping of
    values for columns from the downloaded dataset.
    """
    mapping = store.load(key='cities', auto_download=True).mapping(lhs='city', rhs='state')
    assert len(mapping) == 7
    assert mapping['Troy'] == 'Alabama'
    dataset = store.load(key='cities')
    mapping = dataset.mapping(lhs='city', rhs=['city'])
    assert len(mapping) == 0
    mapping = dataset.mapping(lhs='city', rhs=['city'], ignore_equal=False)
    assert len(mapping) == 7
    mapping = dataset.mapping(lhs='city', rhs='state', transformer=str.lower)
    assert len(mapping) == 7
    assert mapping['troy'] == 'alabama'
    mapping = dataset.mapping(lhs='city', rhs='state', transformer=(str.lower, str.upper))
    assert len(mapping) == 7
    assert mapping['troy'] == 'ALABAMA'


def test_read_dataset(store):
    """Test reading the content of a downloaded dataset file."""
    with store.open(key='cities', auto_download=True) as f:
        linecount = 0
        for line in f:
            linecount += 1
    assert linecount == 8


def test_sqlite_load(store):
    """Test geo data is downloaded and read correctly"""

    dataset = store.load(key='admins', auto_download=True)

    df = dataset.df()
    assert df.shape == (1000, 14)

    dic = dataset.to_dict()
    assert dic.get('format').get('type') == 'sqlite'
