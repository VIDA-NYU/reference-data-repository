# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Interface for format-specific dataset loaders."""

from abc import ABCMeta, abstractmethod
from typing import IO, List

import pandas as pd

from refdata.base import ColumnDescriptor


class DatasetLoader(metaclass=ABCMeta):
    """The dataset loader reads a given opened file and returns a pandas data
    frame containing the dataset in the file.
    """
    @abstractmethod
    def read(self, file: IO, columns: List[ColumnDescriptor]) -> pd.DataFrame:
        """Read data from a given file handle and return a data frame. The
        schema of the returned data frame follows the given column information.
        That is, the column names in the data frame are the identifier of the
        column descriptors and the order of columns is the same as in the given
        list.

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
        raise NotImplementedError()  # pragma: no cover
