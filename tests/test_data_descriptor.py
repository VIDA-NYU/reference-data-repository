# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the data object descriptors."""

import pytest

from refdata.base import ColumnDescriptor, Descriptor, DatasetDescriptor


# -- Descriptor ---------------------------------------------------------------

def test_invalid_descriptor():
    """Test creating a descriptor from a dictionary with missing identifier."""
    with pytest.raises(ValueError):
        Descriptor({'name': '0000'})


def test_maximal_descriptor():
    """Test the functionality for a descriptor with full information."""
    doc = {
        'id': '0000',
        'name': 'D',
        'description': 'A descriptor',
        'tags': ['x', 'y', 'z']
    }
    d = Descriptor(doc)
    assert d.identifier == '0000'
    assert d.name == 'D'
    assert d.description == 'A descriptor'
    assert d.tags == ['x', 'y', 'z']
    assert d.to_dict() == doc


def test_minimal_descriptor():
    """Test the functionality for a descriptor with minimal information."""
    d = Descriptor({'id': '0000'})
    assert d.identifier == '0000'
    assert d.name == d.identifier
    assert d.description is None
    assert d.tags == list()


# -- Column Descriptor --------------------------------------------------------

def test_invalid_column_descriptor():
    """Test creating a column descriptor from a dictionary with missing
    identifier.
    """
    with pytest.raises(ValueError):
        ColumnDescriptor({'name': '0000'})


def test_maximal_column_descriptor():
    """Test the functionality for a column descriptor with full information."""
    doc = {
        'id': '0000',
        'name': 'C',
        'description': 'A column',
        'dtype': 'text',
        'tags': ['u', 'v']
    }
    c = ColumnDescriptor(doc)
    assert c.identifier == '0000'
    assert c.name == 'C'
    assert c.description == 'A column'
    assert c.dtype == 'text'
    assert c.tags == ['u', 'v']
    assert c.to_dict() == doc


def test_minimal_column_descriptor():
    """Test the functionality for a column descriptor with minimal information."""
    c = ColumnDescriptor({'id': '0000'})
    assert c.identifier == '0000'
    assert c.name == c.identifier
    assert c.description is None
    assert c.dtype is None
    assert c.tags == list()


# -- Dataset escriptor --------------------------------------------------------

def test_invalid_dataset_descriptor():
    """Test creating a dataset descriptor from a dictionary with missing
    identifier.
    """
    with pytest.raises(ValueError):
        DatasetDescriptor({'name': '0000'})


def test_maximal_dataset_descriptor():
    """Test the functionality for a dataset descriptor with full information."""
    doc = {
        'id': '0000',
        'name': 'D1',
        'description': 'A dataset',
        'url': 'mydata.download',
        'format': {
            'type': 'csv',
            'parameters': {
                'delim': '\t'
            }
        },
        'schema': [{'id': 'C1'}, {'id': 'C2'}],
        'tags': ['a', 'b'],
        'author': 'Some One',
        'compression': 'gzip',
        'license': 'MIT',
        'webpage': 'on.the.web'
    }
    d = DatasetDescriptor(doc)
    assert d.identifier == '0000'
    assert d.name == 'D1'
    assert d.url == 'mydata.download'
    assert d.description == 'A dataset'
    assert len(d.columns) == 2
    assert d.columns[0].identifier == 'C1'
    assert d.columns[1].identifier == 'C2'
    assert d.format.is_csv
    assert not d.format.is_json
    assert d.format['delim'] == '\t'
    assert d.author == 'Some One'
    assert d.compression == 'gzip'
    assert d.license == 'MIT'
    assert d.tags == ['a', 'b']
    assert d.webpage == 'on.the.web'
    assert d.to_dict() == doc


def test_minimal_dataset_descriptor():
    """Test the functionality for a dataset descriptor with minimal information."""
    d = DatasetDescriptor({
        'id': '0000',
        'url': 'mydata.download',
        'format': {
            'type': 'json',
            'parameters': {
                'target': 'x'
            }
        },
        'schema': [{'id': 'C1'}]
    })
    assert d.identifier == '0000'
    assert d.url == 'mydata.download'
    assert len(d.columns) == 1
    assert d.columns[0].identifier == 'C1'
    assert not d.format.is_csv
    assert d.format.is_json
    assert d.format['target'] == 'x'
    assert d.name == d.identifier
    assert d.author is None
    assert d.compression is None
    assert d.description is None
    assert d.license is None
    assert d.tags == list()
    assert d.webpage is None
