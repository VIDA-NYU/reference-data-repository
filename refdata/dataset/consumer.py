# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Interface and base classes for data consumer that are used to generate
different types of data objects from a dataset in the data store.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set

import pandas as pd


# -- Interface ----------------------------------------------------------------

class DataConsumer(metaclass=ABCMeta):
    """The data consumer interface is used by the dataset loader to create
    different types of objects from the data in a downloaded dataset files.
    Examples of these data objects are pandas data frames, sets of unique
    values in one or more columns, or mappings of values that are generated
    from the reference tables.

    having different implementations of the data consumer for the different
    types of resulting objects avoids having to read all the data rows first
    and the creating the desired object from them.

    Defines a single consume method that is called by the loader to pass the
    data rows that are being read on to the consumer.
    """
    @abstractmethod
    def consume(self, row: List):
        """Consume a single data row that was read by a data loader. The
        schema of the row depends on the list of columns that is being read
        by the dataset loader.

        Parameters
        ----------
        row: list
            List of column values for row in a dataset that is being read
            by a dataset loader.
        """
        raise NotImplementedError()  # pragma: no cover


# -- Base Implementations -----------------------------------------------------

class DataCollector(DataConsumer):
    """Consumer that collects the rows that are passed on to it by a reader.
    Primarily used for test purposes.
    """
    def __init__(self):
        """Initialize the row buffer."""
        self.data = list()

    def consume(self, row: List):
        """Add the given row to the row buffer.

        Parameters
        ----------
        row: list
            List of column values for row in a dataset that is being read
            by a dataset loader.
        """
        self.data.append(row)


class DataFrameGenerator(DataConsumer):
    """Consumer that is used to create a pandas data frame from the rows that
    are read by a dataset loader.
    """
    def __init__(self, columns: List[str]):
        """Initialize the list of columns in the data frame schema.

        Parameters
        ----------
        columns: list of string
            Name of columns in the resulting data frame. The number of names
            in the list is expected to match the number of values in each of
            the dataset rows that the loader passes on to this consumer.
        """
        self.columns = columns
        self.data = list()

    def consume(self, row: List):
        """Add the given row to the list of rows for the generated data frame.

        Parameters
        ----------
        row: list
            List of column values for row in a dataset that is being read
            by a dataset loader.
        """
        self.data.append(row)

    def to_df(self) -> pd.DataFrame:
        """Get the set of distinct values that has been created by the consumer
        from the dataset rows that the loader has passed on to it.

        Returns
        -------
        pd.DataFrame
        """
        return pd.DataFrame(data=self.data, columns=self.columns)


class DistinctSetGenerator(DataConsumer):
    """Consumer that creates a set of distinct values for the rows that are
    being read by a dataset loader.

    If the loader is reading multiple columns, a tuple of values is generated
    for each row before adding it to the set of distinct values.
    """
    def __init__(self, transformer: Optional[Callable] = None):
        """Initialize the empty set of distinct values and the optional value
        transformer.

        Parameters
        ----------
        transformer: callable, default=None
            Optional transformer function that is evaluated on column values
            before adding them to the set of distinct values.
        """
        self.values = set()
        self.transformer = transformer

    def consume(self, row: List):
        """Add the given row to the internal set of distinct values.

        If the row contains a single value (column), that value is added to the
        set. If the row contains multiple values, a tuple is generated for these
        values which is then added to the set of distinct values that is created
        by the consumer.

        Parameters
        ----------
        row: list
            List of column values for row in a dataset that is being read
            by a dataset loader.
        """
        self.values.add(to_value(row=row, transformer=self.transformer))

    def to_set(self) -> Set:
        """Get the set of distinct values that has been created by the consumer
        from the dataset rows that the loader has passed on to it.

        Returns
        -------
        set
        """
        return self.values


class MappingGenerator(DataConsumer):
    """Consumer that creates a mapping from values in one (or multiple) source
    column(s) of a dataset to values in one (or mmultiple) target column(s).

    Each row that is passed to the consumer is split at a pre-defined index
    position into the values in the left-hand side and right-hand side of the
    mapping. If either side of the mapping involves multiple columns, a tuple
    of values for these columns is added to the mapping.
    """
    def __init__(self, split_at: int, ignore_equal: Optional[bool] = True):
        """Initialize the dictionary for the mapping and the column index that
        separates the values in the left-hand side of the mapping from those in
        the right-hand side.

        If the `ignore_equal` flag is True a mapping from a value to itself
        that would be generated by a consumed row will be ignored and not added
        to the mapping.

        Parameters
        ----------
        split_at: int
            Columns index position at which rows are divided into left-hand side
            and right-hand side of the mapping.
        ignore_equal: bool, default=True
            Exclude mappings from a value to itself from the created mapping.
        """
        self.mapping = dict()
        self.split_at = split_at
        self.ignore_equal = ignore_equal

    def consume(self, row: List):
        """Split the given row at the pre-defined position and add the value(s)
        from the left-hand side (lhs) and right-hand side (rhs).

        Add the resulting mapping lhs -> rhs to the generated mapping if (i) no
        mapping for lhs exists and (ii) lhs is not equal to rhs or the
        ignore_identical is False.

        If a value for lhs exists in the mapping a ValueError is raised if the
        existing mapping maps lsh to a value that is different from rhs.

        Parameters
        ----------
        row: list
            List of column values for row in a dataset that is being read
            by a dataset loader.
        """
        lhs = to_value(row[:self.split_at])
        rhs = to_value(row[self.split_at:])
        # Ignore the row id lhs and rhs are equal and ignore_equal flag is True.
        if lhs == rhs and self.ignore_equal:
            return
        # Raise an error if a mapping for lhs exists for a different target
        # than rhs.
        if lhs in self.mapping:
            if self.mapping[lhs] != rhs:
                msg = 'cannot map {} to {} and {}'.format(lhs, self.mapping[lhs], rhs)
                raise ValueError(msg)
        else:
            self.mapping[lhs] = rhs

    def to_mapping(self) -> Dict:
        """Get the set of distinct values that has been created by the consumer
        from the dataset rows that the loader has passed on to it.

        Returns
        -------
        set
        """
        return self.mapping


# -- Helper Functions ---------------------------------------------------------

def to_value(row: List, transformer: Optional[Callable] = None) -> Any:
    """Convert a given list of values into a scalar value or tuple.

    If the given list contains a single element that element is returned.
    Otherwise, a tuple of the values in the list is returned.

    The optional tranformer is applied to all list values individually.

    Parameters
    ----------
    row: list
        List of column values for row in a dataset.

    Returns
    -------
    any
    """
    row = row if transformer is None else list(map(transformer, row))
    return row[0] if len(row) == 1 else tuple(row)
