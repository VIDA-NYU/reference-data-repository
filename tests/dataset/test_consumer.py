# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the different data consumer."""

import pytest

from refdata.dataset.consumer import DataFrameGenerator, DistinctSetGenerator, MappingGenerator


# List of rows for test purposes.
ROWS = [
    ['alice', 'smith', 23],
    ['alice', 'jones', 25],
    ['bob', 'jackson', 24]
]


def test_data_frame_generator():
    """Test consumer that creates a data frame from a list of rows."""
    consumer = DataFrameGenerator(columns=['fname', 'lname', 'age'])
    for row in ROWS:
        consumer.consume(row)
    df = consumer.to_df()
    assert df.shape == (3, 3)
    assert list(df.columns) == ['fname', 'lname', 'age']
    for i in range(len(ROWS)):
        assert list(df.iloc[i]) == ROWS[i]


def test_distinct_set_generaotr():
    """Test the generator for sets of distinct values from one or more columns
    in a dataset.
    """
    consumer = DistinctSetGenerator()
    for row in ROWS:
        consumer.consume(row[:1])
    assert consumer.to_set() == {'alice', 'bob'}
    consumer = DistinctSetGenerator()
    for row in ROWS:
        consumer.consume(row[:2])
    assert consumer.to_set() == {('alice', 'smith'), ('alice', 'jones'), ('bob', 'jackson')}


def test_include_equal_mapping():
    """Test proper interpretation of the include_equal flag when generating
    mappings.
    """
    consumer = MappingGenerator(split_at=1, ignore_equal=False)
    for row in ROWS:
        consumer.consume([row[0], row[0]])
    assert len(consumer.to_mapping()) == 2
    consumer = MappingGenerator(split_at=1, ignore_equal=True)
    for row in ROWS:
        consumer.consume([row[0], row[0]])
    assert len(consumer.to_mapping()) == 0


def test_invalid_mapping():
    """Ensure an error is raised if an invalid mapping is being generated."""
    consumer = MappingGenerator(split_at=1)
    with pytest.raises(ValueError):
        for row in ROWS:
            consumer.consume(row[:2])


def test_mapping_generator():
    """Test the mapping generator."""
    consumer = MappingGenerator(split_at=2)
    for row in ROWS:
        consumer.consume(row)
    mapping = consumer.to_mapping()
    assert len(mapping) == 3
    assert mapping[('alice', 'smith')] == 23
    assert mapping[('alice', 'jones')] == 25
    assert mapping[('bob', 'jackson')] == 24
