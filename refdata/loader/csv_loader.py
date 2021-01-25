# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Loader for csv files."""

from typing import IO, List

import csv

from refdata.loader.base import DatasetLoader
from refdata.base import FormatDescriptor


class CSVLoader(DatasetLoader):
    """Dataset loader for csv files. The csv loader considers the following
    format settings:

    - header (bool): Flag indicating whether the first row in the data file
      contains the column header (default: True)
    - delim (str): Column delimiter string (default=,)

    TODO: add more settings, based on csv reader parameters.
    """
    def __init__(self, parameters: FormatDescriptor, schema: List[str]):
        """Initialize the format settings and the order of columns in the
        data file.

        Parameters
        ----------
        format: refdata.base.FormatDescriptor
            Dataset format specification.
        parameters: list of string
            Order of columns in the data file. This is a list of column
            identifier as defined in the dataset descriptor.
        """
        # Set header information and the delimiter. By default, files are
        # expected to contain header rows and use ',' as the delimiter.
        self.header = parameters.get('header', True)
        self.delim = parameters.get('delim', ',')
        # Create a mapping of column identifer to thier index position in the
        # schema (rows) in the data file.
        self.col_map = {name: index for index, name in enumerate(schema)}

    def read(self, file: IO, columns: List[str]) -> List[List]:
        """Read the data from the given file handle. The returned rows will
        contain only those values for the columns that are contained in the
        given column list.

        The given list of column identifier is expected to be a subset (or equal)
        of the list of column identifier that were provided as the dataset
        schema when the reader was instantiated. A KeyError is raised if the
        given list contains values that are not in the defined dataset schema.

        Parameters
        ----------
        file: file object
            Open file object.
        columns: list of string
            Identifier of columns that are contained in the output.

        Returns
        -------
        list of list
        """
        reader = csv.reader(file, delimiter=self.delim)
        # Skip the first row the it contains the dataset header.
        if self.header:
            next(reader)
        # Create list of index positions for columns in the output.
        cols = [self.col_map[name] for name in columns]
        # Read rows in the data file and extract the values for the columns
        # that are requested to be in the output.
        data = list()
        for row in reader:
            data.append([row[i] for i in cols])
        return data
