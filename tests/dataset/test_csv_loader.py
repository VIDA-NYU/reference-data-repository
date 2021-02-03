# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the csv file loader."""

from io import StringIO

import pytest

from refdata.base import FormatDescriptor
from refdata.dataset.consumer import DataCollector
from refdata.dataset.csv_loader import CSVLoader


@pytest.mark.parametrize(
    'file,header',
    [
        (StringIO('\n'.join(['x1,x2,x3', 'alice,bob,claire'])), True),
        (StringIO('\n'.join(['alice,bob,claire'])), False)
    ]
)
def test_csv_loader(file, header):
    """Test loading files with and without column header."""
    parameters = FormatDescriptor('csv', {'header': header})
    loader = CSVLoader(parameters, schema=['c1', 'c2', 'c3'])
    data = loader.read(file=file, columns=['c1', 'c2', 'c3'], consumer=DataCollector()).data
    assert len(data) == 1
    assert data[0] == ['alice', 'bob', 'claire']


def test_column_order():
    """Test read data from a subset of columns in different order."""
    loader = CSVLoader(parameters=FormatDescriptor('csv'), schema=['c1', 'c2', 'c3'])
    f = StringIO('\n'.join(['x1,x2,x3', 'alice,bob,claire']))
    data = loader.read(f, columns=['c3', 'c1'], consumer=DataCollector()).data
    assert len(data) == 1
    assert data[0] == ['claire', 'alice']
