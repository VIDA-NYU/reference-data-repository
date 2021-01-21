# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Base classes that provide access to metadata about data objects that are
part of the Reference Data Repository. These base classes represent entries
in the repository index file that follows the format that is defined in the
`schema.yaml` schema specification. The general format of the index is:

"datasets": [
    {
        "id": "unique dataset identifier",
        "name": "human-readable dataset name",
        "description": "optional short description of dataset content",
        "author": "optional author/owner information",
        "license": "optional dataset license identifier",
        "url": "download url for the data file",
        "webpage": "optional web page containing additional information about the dataset",
        "compression": "optional identifier for data compression algorithm, e.g., 'gzip'",
        "schema": [
            {
                "id": "unique column identifier",
                "name": "optional human-readable column name",
                "description": "short descriptive text for the column type",
                "dtype": "optional column data type information",
                "tags": ["list of semantic tag strings describing the column"]
            }
        ],
        "format": {
            "id": "format type identifier, e.g., 'csv, 'json, 'sqlite', ...",
            "parameters": {
                "Format specific properties that are used as parameters for the
                dataset loader."
            }
        },
        "tags": ["list of semantic tag strings describing the dataset"]
    }
]

"""

from __future__ import annotations
from typing import Dict, List, Set


class Descriptor:
    """The descriptor base class provides access to the basic metadata for all
    data objects in the repository. This metadata includes the mandatory object
    identifier, as well as the optional name, description, and list of tags.
    """
    def __init__(self, doc: Dict):
        """Initialize the descriptor from a given data object dictionary
        serialization. Expects a dictionary that contains at least an 'id'
        element.

        Raises a ValueError if the given dictionary does not contain the
        pbject identifier.

        Paramaters
        ----------
        doc: dict
            Dictionary serialization for a dataset object in the repository.
        """
        if 'id' not in doc:
            raise ValueError('missing identifier in {}'.format(doc))
        self.doc = doc

    @property
    def description(self) -> str:
        """Get the optional description. The result is None if no description
        was provided for the object.

        Returns
        -------
        string
        """
        return self.doc.get('description')

    @property
    def identifier(self) -> str:
        """Get the unique object identifier. Raises a KeyError if the mandatory
        identifier is not present in the dictionary serialization object.

        Returns
        -------
        string
        """
        return self.doc['id']

    @property
    def name(self) -> str:
        """Get the object name. If the name is not present in the dictionary
        serialization the object identifier is returned as the default.

        Returns
        -------
        string
        """
        return self.doc.get('name', self.doc['id'])

    @property
    def tags(self) -> List[str]:
        """Get the list of tags that define the semantics of the data object.
        The result is an empty list if no tag information is included in the
        dictionary serialization for the object.

        Returns
        -------
        string
        """
        return self.doc.get('tags', list())

    def to_dict(self) -> Dict:
        """Get the dictionary serialization for the object.

        Returns
        -------
        dict
        """
        return self.doc


class ColumnDescriptor(Descriptor):
    """Descriptor for a dataset column. Provides access to the column identifier,
    name, description, data type, and tags. This is a wrapper around a
    dictionary serialization for the column from the dataset entry in the
    global repository index.
    """
    def __init__(self, doc: Dict):
        """Initialize the descriptor from the object serialization. Expects a
        dictionary that follows the schema of the ColumnDescriptor in the
        repository index format specification.

        Parameters
        ----------
        doc: dict
            Dictionary serialization for a dataset columns.
        """
        super(ColumnDescriptor, self).__init__(doc=doc)

    @property
    def dtype(self) -> str:
        """Get the optional column data type identifier. The result is None if
        no type information was provided for the columns.

        Returns
        -------
        string
        """
        return self.doc.get('dtype')


class DatasetDescriptor(Descriptor):
    """The descriptor provides access to the dataset metadata. This is a wrapper
    around the dataset entry in the global repository.
    """
    def __init__(self, doc: Dict):
        """Create an instance of the dataset descriptor class from a given
        dictionary serialization. Expects that the elements in the dictionary
        follow the DatasetDescriptor schema from the index format specification.

        Paramaters
        ----------
        doc: dict
            Dictionary serialization for a dataset in the repository.
        """
        super(DatasetDescriptor, self).__init__(doc=doc)
        # Keep set of tags for dataset and all columns for query purposes. This
        # set is intialized when accessed for the first time.
        self._tags = None

    @property
    def author(self) -> str:
        """Get the dataset author information.

        Returns
        -------
        string
        """
        return self.doc.get('author')

    @property
    def columns(self) -> List[ColumnDescriptor]:
        """Get the list of descriptors for the columns in the dataset schema.
        Raises a KeyError if the mandatory schema information is not present
        in the dictionary serialization object.

        Returns
        -------
        list of refdata.base.ColumnDescriptor
        """
        return [ColumnDescriptor(c) for c in self.doc['schema']]

    @property
    def compression(self) -> str:
        """Get the dataset compression information.

        Returns
        -------
        string
        """
        return self.doc.get('compression')

    @property
    def format(self) -> FormatDescriptor:
        """Get the format specification for the dataset. Raises a KeyError if
        the mandatory format is not present in the dictionary serialization
        object.

        Returns
        -------
        refdata.base.FormatDescriptor
        """
        obj = self.doc['format']
        return FormatDescriptor(type=obj['type'], parameters=obj['parameters'])

    @property
    def license(self) -> str:
        """Get the dataset license information.

        Returns
        -------
        string
        """
        return self.doc.get('license')

    def matches(self, query: Set[str]) -> bool:
        """Evaluate query on dataset tags. Returns True if the set of tags for
        the dataset and all its columns include the tages in the given query.

        Parameters
        ----------
        query: set of string
            Set of query tags.

        Returns
        -------
        bool
        """
        # Initialize the full set of tags when accessed for the first time.
        if self._tags is None:
            self._tags = set(self.tags)
            for c in self.columns:
                self._tags.update(c.tags)
        # The dataset is a match if the query is a subset of the full tag set.
        return query.issubset(self._tags)

    @property
    def url(self) -> str:
        """Get the download Url for the dataset. Raises a KeyError if the
        mandatory url is not present in the dictionary serialization object.

        Returns
        -------
        string
        """
        return self.doc['url']

    @property
    def webpage(self) -> str:
        """Get the optional dataset web page information.

        Returns
        -------
        string
        """
        return self.doc.get('webpage')


class FormatDescriptor(dict):
    """Dataset format descriptor extends a dictionary for format parameters
    with properties for the dataset type format.
    """
    def __init__(self, type: str, parameters: Dict):
        """Initialize the dataset format identifier and set the format
        parameters.

        Parameters
        ----------
        type: string
            Dataset format type identifier.
        parameters: dict
            Dictionary for format-specific settings.
        """
        super(FormatDescriptor, self).__init__(**parameters)
        self.format_type = type

    @property
    def is_csv(self) -> bool:
        """True if the dataset is of type 'csv'.

        Returns
        -------
        bool
        """
        return self.format_type == 'csv'

    @property
    def is_json(self) -> bool:
        """True if the dataset is of type 'json'.

        Returns
        -------
        bool
        """
        return self.format_type == 'json'
