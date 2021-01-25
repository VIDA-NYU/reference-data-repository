# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Loader implementation for datasets that are given in Json format."""

from typing import Any, Dict, IO, List

import json

from refdata.base import FormatDescriptor
from refdata.loader.base import DatasetLoader


class JsonLoader(DatasetLoader):
    """Dataset loader for Json files. The dataset is assumed to be a list of
    dictionaries, where each dictionary represents one row in the dataset.
    This list of dictionary may be contained in another dictionary. In this
    case the target path in the format settings references the list element.
    For each column, the column identifier from the dataset schema is
    expected to be the query path to extract the respective cell value from
    a dictionary representing a dataset row. This default behavior can be
    overriden by including an object {'id': 'column-id', 'path': 'query path'}
    for that column in the 'sources' element of the format settings.

    The Json loader considers the following settings:

    - target (string): Path to the list element containing the data row
      dictionaries (default='').
    - sources (list): List of {'id', 'path'}-pairs defining the query path
      extract cell values for individual columns.
    """
    def __init__(self, parameters: FormatDescriptor):
        """Initialize the format settings.

        Parameters
        ----------
        parameters: refdata.base.FormatDescriptor
            Dataset format specification.
        """
        # Set the arget query to extract the dataset rows from the document.
        self.target = JQuery(parameters.get('target', ''))
        # Create mapping of column identifier to their source path for the
        # columns that have a source path that is different from thier
        # identifier. Columns fow which no entry exists in the 'sources' list
        # the source path is expected to be the column identifier.
        self.source_map = {s['id']: s['path'] for s in parameters.get('sources', dict())}

    def read(self, file: IO, columns: List[str]) -> List[List]:
        """Read dataset rows from a given file handle.

        Assumes that the file contains a Json object. This methof first extracts
        the list of dataset row objects from the Json object in the file. It
        then creates a dataset row from each object based on the source path for
        each column in the given column list.

        If no source path was list of objects identfied by the data target path that
        was defined in the dataset format.

        Parameters
        ----------
        file: file object
            Open file object.
        columns: list of string
            Column identifier defining the content and the schema of the
            returned data.

        Returns
        -------
        list of list
        """
        # Create the list of source queries for each column in the resulting
        # dataset rows. Use the column to source mapping that was created from
        # the format parameters when the object was instantiated. By default,
        # the column identifier is used as the query path.
        sources = list()
        for col in columns:
            sources.append(JQuery(self.source_map.get(col, col)))
        data = list()
        for doc in self.target.find(json.load(file)):
            data.append([q.find(doc) for q in sources])
        return data


# -- Helper Functions ---------------------------------------------------------

class JQuery:
    """Helper class to evaluate path expressions on nested dictionaries."""
    def __init__(self, path: str):
        """Initialize the query path. The path is a string with individual
        path components separated by '/'.

        Parameters
        ----------
        query: string
            Query path expression.
        """
        # Remove trailing '/' from the path.
        while path.endswith('/'):
            path = path[:-1]
        # Ensure that the query path is an empty list if the path is empty.
        self.path = path.split('/') if path else []

    def find(self, doc: Dict[str, Any]) -> Any:
        """Get the element at the query path in the given nested dictionary.
        
        Returns None if the query path does not identify an element in the
        given dictionary.

        Parameters
        ----------
        doc: dict
            Nested dictionary object.

        Returns
        -------
        any
        """
        # Keep track of the depth of the (successfully) evaluated part of the
        # query path.
        depth = 0
        while depth < len(self.path) and isinstance(doc, dict):
            doc = doc.get(self.path[depth])  # type: ignore
            depth += 1
        # The result depends on whether we reaced the end of the path (depth
        # equals length of the query path) or encountered an element in the
        # query path that was not matched (depth is less than the length of
        # the query path). In the latter case the result is always None.
        return doc if depth == len(self.path) else None
