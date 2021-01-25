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

from refdata.loader.consumer import DataConsumer


class DatasetLoader(metaclass=ABCMeta):
    """Interface for the dataset loader that are used to read data from
    downloaded data files. Each data format that is supported by the repository
    provides their own format-specific implementation of the data loader. The
    loader is associated with, and instantiated in, the handle for a dataset.
    """
    @abstractmethod
    def read(self, file: IO, columns: List[str], consumer: DataConsumer) -> DataConsumer:
        """Read data from a given file handle.

        The schema and content of the read rows is defined by the given list of
        column identifier. The rows are passed on to a given consumer.

        The file handle represents the opened data file for a dataset that has
        been downloaded from the repository to the local data store. The list
        of columns contains identifier for columns that are defined in the
        dataset descriptor. The read rows contain only those columns that are
        defined in the given list.

        Returns a reference to the given data consumer.

        Parameters
        ----------
        file: file object
            Open file object.
        columns: list of string
            Column identifier defining the content and the schema of the
            returned data.
        consumer: refdata.loader.consumer.DataConsumer
            Consumer for data rows that are being read.

        Returns
        -------
        refdata.loader.consumer.DataConsumer
        """
        raise NotImplementedError()  # pragma: no cover
