# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the csv file loader."""

from io import StringIO

import pytest

from refdata.base import ColumnDescriptor, FormatDescriptor
from refdata.loader.csv_loader import CSVLoader


"""Test schema with three columns."""
SCHEMA = [
    ColumnDescriptor({'id': 'c1', 'name': 'Col1'}),
    ColumnDescriptor({'id': 'c2', 'name': 'Col2'}),
    ColumnDescriptor({'id': 'c3', 'name': 'Col3'})
]


@pytest.mark.parametrize(
    'file,header',
    [
        (StringIO('\n'.join(['x1,x2,x3', 'alice,bob,claire'])), True),
        (StringIO('\n'.join(['alice,bob,claire'])), False)
    ]
)
def test_csv_loader(file, header):
    """Test loading files with and without column header."""
    format = FormatDescriptor('csv', {'header': header})
    df = CSVLoader(format).read(file=file, columns=SCHEMA)
    assert df.shape == (1, 3)
    assert list(df.columns) == [c.identifier for c in SCHEMA]
    assert list(df.iloc[0]) == ['alice', 'bob', 'claire']
