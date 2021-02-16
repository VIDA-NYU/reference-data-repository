# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The repository manager provides access to the list of datasets that are
available for download in the Reference Data Repository.
"""

from typing import Dict, List, Optional, Set, Union

from refdata.base import DatasetDescriptor


class RepositoryManager:
    """The repository manager provides the functionality for querying a
    dataset index. The index is intialized when the manager is created.
    By default, the index that the environment variable REFDATA_URL or
    its default value points to is read.
    """
    def __init__(self, doc: Dict):
        """Initialize the index of dataset descriptors.

        Parameters
        ----------
        doc: dict
            Dictionary containing the dataset index. This dictionary is
            expected to follow the `RepositoryIndex` schema.
        """
        # Create dataset index for entries in the read document.
        self.datasets = dict()
        for obj in doc.get('datasets', list()):
            ds = DatasetDescriptor(obj)
            self.datasets[ds.identifier] = ds

    def find(self, filter: Optional[Union[str, List[str], Set[str]]] = None) -> List[DatasetDescriptor]:
        """Query the dataset index. The filter is a single tag or a list of
        tags. The result will contain those datasets that contain all the
        query tags. The search includes the dataset tags as well a the tags
        for individual dataset columns.

        If no filter is specified the full list of datasets descriptors in the
        repository is returned.

        Parameters
        ----------
        filter: string, list of string, or set of string
            (List of) query tags.

        Returns
        -------
        list of refdata.base.DatasetDescriptor
        """
        # Return the full list of descriptors if the filter is None.
        if filter is None:
            return list(self.datasets.values())
        # Ensure that filter is a set.
        if not isinstance(filter, set):
            filter = set(filter) if isinstance(filter, list) else set([filter])
        # Find all datasets that include all tags in the list.
        result = list()
        for ds in self.datasets.values():
            if ds.matches(query=filter):
                result.append(ds)
        return result

    def get(self, key: str) -> DatasetDescriptor:
        """Get the descriptor for the dataset with the given identifier. If no
        dataset with that identifier exists the result is None.

        Parameters
        ----------
        key: string
            Unique dataset identifier

        Returns
        -------
        refdata.base.DatasetDescriptor
        """
        return self.datasets.get(key)
