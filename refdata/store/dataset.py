# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

from typing import Dict

import gzip
import pandas as pd

from refdata.base import DatasetDescriptor
from refdata.loader import CSVLoader, JsonLoader

import refdata.error as err


class DatasetHandle(DatasetDescriptor):
    """Handle for a dataset in the local data store. Provides the functionality
    to load the dataset as a pandas data frame.
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
        format = self.format
        if format.is_csv:
            self.loader = CSVLoader(format)
        elif format.is_json:
            self.loader = JsonLoader(format)
        else:
            raise err.InvalidFormatError("unknown format '{}'".format(format.format_type))

    def load(self) -> pd.DataFrame:
        """Load the dataset as a pandas data frame.

        Returns
        -------
        pd.DataFrame
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
            return self.loader.read(f)
        finally:
            f.open()
