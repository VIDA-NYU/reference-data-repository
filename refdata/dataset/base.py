# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

from typing import Dict, List, Optional, Set, Union

import gzip
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
    def __init__(self, doc: Dict, datafile: str):
        """Initialize the descriptor information and the path to the downloaded
        data file. This will also create an instance of the dataset loader that
        is dependent on the dataset format.

        Parameters
        ----------
        doc: dict
            Dictionary serialization for the dataset descriptor.
        datafile: string
            Path to the downloaded file.
        """
        super(DatasetHandle, self).__init__(doc=doc)
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

    def data_frame(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
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

    def distinct(self, columns: Optional[Union[str, List[str]]] = None) -> Set:
        """Get the set of distinct values from the specified column(s) in the
        dataset.

        This is a shortcut to load column values using the distinct set generator
        as the data consumer. If no columns are specified the set of distinct
        rows is returned.

        If more than one column is specified the elements in the returned set
        are tuples of values.

        Parameters
        ----------
        columns: string or list of string, default=None
            Column identifier defining the values that are added to the
            generated set of distinct values.

        Returns
        -------
        set
        """
        # If columns are not specified use the full list of columns that are
        # defined in the dataset descriptor.
        columns = columns if columns is not None else [c.identifier for c in self.columns]
        # Ensure that columns are a list.
        columns = columns if isinstance(columns, list) else [columns]
        return self.load(columns=columns, consumer=DistinctSetGenerator()).to_set()

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
        ignore_equal: Optional[bool] = True
    ) -> Dict:
        """Generate a mapping from values in dataset rows.

        The generated mapping maps values for each row from columns in the
        left-hand side expression to their respective counerparts in the right-hand
        side expression.

        This is a shortcut to load column values using the mapping generator
        as the data consumer.

        Parameters
        ----------
        lhs: string or list of string
            Columns defining the source of values for the left-hand side of the
            mapping.
        rhs: string or list of string
            Columns defining the source of values for the right-hand side of the
            mapping.
        ignore_equal: bool, default=True
            Exclude mappings from a value to itself from the created mapping.

        Returns
        -------
        set
        """
        # Ensure that lhs and rhs are lists.
        lhs = lhs if isinstance(lhs, list) else [lhs]
        rhs = rhs if isinstance(rhs, list) else [rhs]
        consumer = MappingGenerator(split_at=len(lhs), ignore_equal=ignore_equal)
        return self.load(columns=lhs + rhs, consumer=consumer).to_mapping()
