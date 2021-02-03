# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the Json file loader."""

import pytest

from refdata.dataset.base import DatasetHandle
from refdata.dataset.consumer import DataCollector
from refdata.dataset.json_loader import JQuery


# -- Loader -------------------------------------------------------------------

DESCRIPTOR = {
    "id": "countries",
    "name": "REST Countries",
    "description": "Information about countries in the world available from the restcountries.eu project.",
    "url": "countries.json",
    "checksum": "889c264f2ac4629b4998aa8b8b1d4de45890c39c10e24cfd8a017e9924e805c7",
    "schema": [
        {"id": "name"},
        {"id": "alpha2Code"},
        {"id": "alpha3Code"},
    ]
}


@pytest.mark.parametrize(
    'parameters,columns,first_row',
    [
        (
            {"type": "json", "parameters": {}},
            ['name', 'alpha2Code', 'alpha3Code'],
            ['Afghanistan', 'AF', 'AFG']
        ),
        (
            {"type": "json", "parameters": {}},
            ['alpha2Code', 'name', 'alpha3Code'],
            ['AF', 'Afghanistan', 'AFG']
        ),
        (
            {
                "type": "json",
                "parameters": {'sources': [
                    {'id': 'name', 'path': 'alpha2Code'},
                    {'id': 'alpha2Code', 'path': 'alpha3Code'},
                    {'id': 'alpha3Code', 'path': 'capital'}
                ]}
            },
            ['name', 'alpha2Code', 'alpha3Code'],
            ['AF', 'AFG', 'Kabul']
        )
    ]
)
def test_json_loader(parameters, columns, first_row, countries_file, mock_response):
    descriptor = dict(DESCRIPTOR)
    descriptor['format'] = parameters
    dataset = DatasetHandle(doc=descriptor, datafile=countries_file)
    data = dataset.load(columns=columns, consumer=DataCollector()).data
    assert len(data) == 2
    assert data[0] == first_row


# -- JQuery -------------------------------------------------------------------

# Input document for JQuery tests.

DOC = {
    'a': {
        'b': {
            'c': 1
        },
        'c': 2,
        'd': [
            {'c': 3}
        ]
    }
}


@pytest.mark.parametrize(
    'path,result',
    [
        ('a/b', {'c': 1}),
        ('a/b/c', 1),
        ('a/b/c/', 1),
        ('a/c', 2),
        ('a/d/c', None),
        ('a/e', None),
        ('e', None),
        ('e/', None),
        ('', DOC),
        ('///', DOC)
    ]
)
def test_json_query(path, result):
    """Test evaluating different path expressions on a nested dictionary."""
    assert JQuery(path=path).find(DOC) == result
