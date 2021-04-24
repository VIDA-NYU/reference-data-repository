# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Loader implementation for datasets that are given in MySQL format."""

from typing import List

import sqlite3

from refdata.base import FormatDescriptor
from refdata.dataset.consumer import DataConsumer
from refdata.dataset.loader import DatasetLoader
from refdata.error import InvalidFormatError


class MySQLLoader(DatasetLoader):
    """Dataset loader for MySQL files.
    """
    def __init__(self, parameters: FormatDescriptor):
        """Initialize the format settings and the order of columns in the
        data file.

        Parameters
        ----------
        parameters: refdata.base.FormatDescriptor
            Dataset format specification.
        """
        self.table = parameters.get('table')
        if self.table is None:
            InvalidFormatError("Missing schema (table) name in format type '{}'".format(parameters.format_type))

    def read(self, file: str, columns: List[str], consumer: DataConsumer) -> DataConsumer:
        """Read dataset rows from a given file handle.

        Assumes that the file contains a path str. This method iterates over the mysqllite
        cursor and passes each row to the consumer

        Parameters
        ----------
        file: string
            string path of file.
        columns: list of string
            Column identifier defining the content and the schema of the
            returned data.
        consumer: refdata.dataset.consumer.DataConsumer
            Consumer for data rows that are being read.

        Returns
        -------
        list of list
        """

        # Create a SQL connection to our SQLite database
        con = sqlite3.connect(file)

        cur = con.cursor()

        # The result of a "cursor.execute" can be iterated over by row
        for row in cur.execute('SELECT * FROM {}'.format(self.table)):
            consumer.consume(row)

        # Be sure to close the connection
        con.close()

        return consumer
