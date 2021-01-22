# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Loader for csv files."""

from typing import IO, List

import pandas as pd

from refdata.loader.base import DatasetLoader
from refdata.base import ColumnDescriptor, FormatDescriptor


class CSVLoader(DatasetLoader):
    """Dataset loader for csv files. The csv loader considers the following
    format settings:

    - header (bool): Flag indicating whether the first row in the data file
      contains the column header (default: True)
    - delim (str): Column delimiter string (default=,)

    TODO: add more settings, based on csv reader and pandas read_csv.
    """
    def __init__(self, format: FormatDescriptor):
        """Initialize the format settings.

        Parameters
        ----------
        format: refdata.base.FormatDescriptor
        """
        # The loader uses pandas' read_csv method to create the data frame.
        # Use header=0 to override column names if the input file has a
        # header row.
        self.header = 0 if format.get('header', True) else None
        self.delim = format.get('delim', ',')

    def read(self, file: IO, columns: List[ColumnDescriptor]) -> pd.DataFrame:
        """Read the data frame from the given file handle. If the file contains
        a column header that header is ignored. The names of columns in the
        returned schema are the identifier of the column descriptors in the
        given list.

        Parameters
        ----------
        file: file object
            Open file object.
        columns: list of refdata.base.ColumnDescriptor
            Columns descriptors defining the schema of the returned data frame.

        Returns
        -------
        pd.DataFrame
        """
        return pd.read_csv(
            file,
            sep=self.delim,
            names=[c.identifier for c in columns],
            header=self.header
        )
