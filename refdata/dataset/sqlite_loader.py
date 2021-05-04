# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Loader implementation for datasets that are given in SQLite format."""

from typing import List

import sqlite3

from refdata.base import FormatDescriptor
from refdata.dataset.consumer import DataConsumer
from refdata.dataset.loader import DatasetLoader
from refdata.error import InvalidFormatError


class SQLiteLoader(DatasetLoader):
    """Dataset loader for SQLite files.
    """
    def __init__(self, parameters: FormatDescriptor):
        """Initialize the sql queries to run on the database. If both the query and table parameters are present,
        it will use the query else it will deduce a generic query from the table name.

        Parameters
        ----------
        parameters: refdata.base.FormatDescriptor
            Dataset format specification.
        """
        self.query = parameters.get('query')
        self.table = parameters.get('table')
        if self.query is None and self.table is None:
            InvalidFormatError("Missing schema (table) name in format type '{}'".format(parameters.format_type))
        elif self.query is None:
            self.query = 'SELECT * FROM {}'.format(self.table)

    def read(self, file: str, columns: List[str], consumer: DataConsumer) -> DataConsumer:
        """Read dataset rows from a given file handle.

        Assumes that the file contains a path str. This method iterates over the sqlite
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
        for row in cur.execute(self.query):
            consumer.consume(row)

        # Be sure to close the connection
        con.close()

        return consumer
