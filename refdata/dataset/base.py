# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Base classes for handles that provide access to datasets that have been
downloaded to the local data store.
"""

from dateutil.parser import isoparse
from typing import Callable, Dict, IO, List, Optional, Set, Tuple, Union

import datetime
import gzip
import os
import pandas as pd

from refdata.base import DatasetDescriptor
from refdata.dataset.consumer import DataConsumer, DataFrameGenerator, DistinctSetGenerator, MappingGenerator
from refdata.dataset.csv_loader import CSVLoader
from refdata.dataset.json_loader import JsonLoader

import refdata.error as err


class DatasetHandle(DatasetDescriptor):
    """Handle for a dataset in the local data store. Provides the functionality
    to read data in different formats from the downloaded data file.
    """
    def __init__(
        self, descriptor: Dict, package_name: str, package_version: str,
        created_at: datetime.datetime, datafile: str
    ):
        """Initialize the descriptor information and the path to the downloaded
        data file.

        This will also create an instance of the dataset loader that is used
        for reading the data file dependent on the dataset format.

        Parameters
        ----------
        descriptor: dict
            Dictionary serialization for the dataset descriptor.
        package_name: string
            Name of the package that downloaded the dataset.
        package_version: string
            Version information for the package that downloaded the dataset.
        created_at: str
            Timestamp (in UTC) when the dataset was downloaded.
        datafile: string
            Path to the downloaded file.
        """
        super(DatasetHandle, self).__init__(doc=descriptor)
        self.package_name = package_name
        self.package_version = package_version
        # Convert the timestamp from UTC to local time.
        self.created_at = isoparse(created_at).astimezone()
        self.datafile = datafile
        # Create the format-dependent instance of the dataset loader.
        parameters = self.format
        if parameters.is_csv:
            self.loader = CSVLoader(
                parameters=parameters,
                schema=[c.identifier for c in self.columns]
            )
        elif parameters.is_json:
            self.loader = JsonLoader(parameters)
        else:
            raise err.InvalidFormatError("unknown format '{}'".format(parameters.format_type))

    def df(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load dataset as a pandas data frame.

        This is a shortcut to load all (or a given selection of) columns in
        the dataset as a pandas data frame. If the list of columns is not
        given the full dataset is returned.

        Parameters
        ----------
        columns: list of string, default=None
            Column identifier defining the content and the schema of the
            returned data frame.

        Returns
        -------
        pd.DataFrame
        """
        # If columns are not specified use the full list of columns that are
        # defined in the dataset descriptor.
        columns = columns if columns is not None else [c.identifier for c in self.columns]
        consumer = DataFrameGenerator(columns=columns)
        return self.load(columns=columns, consumer=consumer).to_df()

    def distinct(
        self, columns: Optional[Union[str, List[str]]] = None,
        transformer: Optional[Callable] = None
    ) -> Set:
        """Get the set of distinct values from the specified column(s) in the
        dataset.

        This is a shortcut to load column values using the distinct set generator
        as the data consumer. If no columns are specified the set of distinct
        rows is returned.

        If more than one column is specified the elements in the returned set
        are tuples of values.

        If the optional transformer is given it will be evaluated on the individual
        values that are extracted from the columns before adding them to the set
        of unique values.

        Parameters
        ----------
        columns: string or list of string, default=None
            Column identifier defining the values that are added to the
            generated set of distinct values.
        transformer: callable, default=None
            Optional transformer function that is evaluated on column values
            before adding them to the set of distinct values.

        Returns
        -------
        set
        """
        # If columns are not specified use the full list of columns that are
        # defined in the dataset descriptor.
        columns = columns if columns is not None else [c.identifier for c in self.columns]
        # Ensure that columns are a list.
        columns = columns if isinstance(columns, list) else [columns]
        consumer = DistinctSetGenerator(transformer=transformer)
        return self.load(columns=columns, consumer=consumer).to_set()

    @property
    def filesize(self) -> int:
        return os.stat(self.datafile).st_size

    def load(self, columns: List[str], consumer: DataConsumer) -> DataConsumer:
        """Load data for the specified columns from the downloaded dataset
        file.

        The list of columns is expected to contain only identifier for columns
        in the schema that is defined in the dataset descriptor.

        Read rows are passed on to the given consumer. A reference to that
        consumer is returned.

        Parameters
        ----------
        columns: list of string
            Column identifier defining the content and the schema of the
            returned data.
        consumer: refdata.dataset.consumer.DataConsumer
            Consumer for data rows that are being read.

        Returns
        -------
        refdata.dataset.consumer.DataConsumer
        """
        # Open the file depending on whether it is compressed or not. By now,
        # we only support gzip compression.
        if self.compression == 'gzip':
            f = gzip.open(self.datafile, 'rt')
        else:
            f = open(self.datafile, 'rt')
        # Use the format-specific loader to get the data frame. Ensure to close
        # the opened file when done.
        try:
            return self.loader.read(f, columns=columns, consumer=consumer)
        finally:
            f.close()

    def mapping(
        self, lhs: Union[str, List[str]], rhs: Union[str, List[str]],
        transformer: Optional[Union[Callable, Tuple[Callable, Callable]]] = None,
        ignore_equal: Optional[bool] = True
    ) -> Dict:
        """Generate a mapping from values in dataset rows.

        The generated mapping maps values for each row from columns in the
        left-hand side expression to their respective counerparts in the right-hand
        side expression.

        This is a shortcut to load column values using the mapping generator
        as the data consumer.

        It the optional transformer is given it is evaluated on column values
        before adding them to the mapping. If a single callable is given, that
        function is evalauated on the lhs and rhs columns. If a 2-tuple of
        callables is given, the first function is evalauted on lhs columns and
        the second function on rhs. columns.

        Parameters
        ----------
        lhs: string or list of string
            Columns defining the source of values for the left-hand side of the
            mapping.
        rhs: string or list of string
            Columns defining the source of values for the right-hand side of the
            mapping.
        transformer: callable or tuple of callable, default=None
            Optional transformer function(s) that are evaluated on the values
            for lhs and rhs columns before adding them to the mapping.
        ignore_equal: bool, default=True
            Exclude mappings from a value to itself from the created mapping.

        Returns
        -------
        set
        """
        # Ensure that lhs and rhs are lists.
        lhs = lhs if isinstance(lhs, list) else [lhs]
        rhs = rhs if isinstance(rhs, list) else [rhs]
        consumer = MappingGenerator(
            split_at=len(lhs),
            transformer=transformer,
            ignore_equal=ignore_equal
        )
        return self.load(columns=lhs + rhs, consumer=consumer).to_mapping()

    def open(self) -> IO:
        """Open the downloaded data file for the dataset.

        Returns
        -------
        file-like object
        """
        # Open the file depending on whether it is compressed or not. By now,
        # we only support gzip compression.
        if self.compression == 'gzip':
            return gzip.open(self.datafile, 'rt')
        else:
            return open(self.datafile, 'rt')
