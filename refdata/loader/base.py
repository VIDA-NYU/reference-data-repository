# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Interface for format-specific dataset loader. For each data format that is
supported by the Reference Data Repository a format-specific implementation of
the loader interface needs to be provided.
"""

from abc import ABCMeta, abstractmethod
from typing import IO, List


class DatasetLoader(metaclass=ABCMeta):
    """Interface for the dataset loader that are used to read data from
    downloaded data files. Each data format that is supported by the repository
    provides their own format-specific implementation of the data loader. The
    loader is associated with, and instantiated in, the handle for a dataset.
    """
    @abstractmethod
    def read(self, file: IO, columns: List[str]) -> List[List]:
        """Read data from a given file handle.

        Returns a list of data rows. The schema and content of the returned
        rows is defined by the given list of column identifier.

        The file handle represents the opened data file for a dataset that has
        been downloaded from the repository to the local data store. The list
        of columns contains identifier for columns that are defined in the
        dataset descriptor. The returned rows contain only those columns that
        are defined in the given schema.

        Parameters
        ----------
        file: file object
            Open file object.
        columns: list of string
            Column identifier defining the content and the schema of the
            returned data.

        Returns
        -------
        list of lists
        """
        raise NotImplementedError()  # pragma: no cover
