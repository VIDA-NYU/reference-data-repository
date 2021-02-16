# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""The repository loader serves two purposes. First, it provides an interface
for loading (or creating) repository indexes from different sources (e.g., from
an Url or a file on the local file system) and (if required) in different
formats than the official repository index schema. Second, it supports deferred
loading of the dataset index. Deferred loading is used by the local data store
to defer loading of the associated repository index until it is first being
accesed.

This module provides default implementations for loading a repository index
in the default schema from an Url, a local file, or from a dictionary. It also
provides implementations for the loader of a federated index file and the
loader for the default federated index.
"""


from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

import json
import requests
import yaml

import refdata.config as config


"""Definition of valid file format identifier."""
FORMAT_JSON = 'json'
FORMAT_YAML = 'yaml'
FILE_FORMATS = [FORMAT_JSON, FORMAT_YAML]


class RepositoryIndexLoader(metaclass=ABCMeta):
    """Interface for the repository index loader.

    Provides a single method `load` that is expected to return a dictionary
    containing a list of dataset descriptors that adheres to the `RepositoryIndex`
    structure defined in the repository schema.

    Different implementations will (a) read the data from different sources,
    and (b) transform the read data if necessary into the expected format.
    """
    @abstractmethod
    def load(self) -> Dict:
        """Load a repository index from a data source.

        Returns a dictionary that adheres to the `RepositoryIndex` structure
        defined in the repository schema.

        Returns
        -------
        dict
        """
        raise NotImplementedError()  # pragma: no cover


# -- Helper Functions ---------------------------------------------------------

class DictLoader(RepositoryIndexLoader):
    """Repository index loader that is a wrapper around a dictionary containing
    a list of serialized file descriptors. Loading the index will simply return
    the wrapped dictionary.
    """
    def __init__(self, doc: Dict):
        """Initialize the dictionary containing the serialized repository index.

        Parameters
        ----------
        doc: dict
            Dictionary containing a single element `datasets` with a list of
            serialized dataset descriptors.
        """
        self.doc = doc

    def load(self) -> Dict:
        """Loading the repository index will return the dictionary that was
        given when the object was instantiated.

        Returns
        -------
        dict
        """
        return self.doc


class FileLoader(RepositoryIndexLoader):
    """Load repository index from a file on the local file system.

    Supports loading files in Json or YAML format. The file format is specified
    as as an optional argument with file types being identified as `json` or
    `yaml`. If the file format argument is not given an attempt is made to
    guess the format from the file suffix. The default format is `json`.

    The file loader currently does not follow references to federated
    repositories that may be listed in optional `repositories` element of the
    loaded index file.
    """
    def __init__(self, filename: str, ftype: Optional[str] = None):
        """Initialize the path to the file containing the repository index and
        the optional file format identifier.

        Raises a ValueError if an invalid file format is given. Valid format
        identifier are `json` or `yaml`.

        Parameters
        ----------
        filename: string
            Path to file on the file system.
        ftype: string, default='json'
            Identifier for the file format.
        """
        self.filename = filename
        self.ftype = get_file_format(ftype=ftype, filename=filename)

    def load(self) -> Dict:
        """Read repository index from file.

        Returns
        -------
        dict
        """
        with open(self.filename, 'r') as f:
            if self.ftype == FORMAT_YAML:
                return yaml.load(f.read(), Loader=yaml.FullLoader)
            else:
                return json.load(f)


class UrlLoader(RepositoryIndexLoader):
    """Repository index loader that reads data from a given Url.

    Uses the Url that is specified in the environment variable *REFDATA_URL* if
    no Url is given when the class is initialized.

    Supports loading files in Json or YAML format. The file format is specified
    as as an optional argument with file types being identified as `json` or
    `yaml`. If the file format argument is not given an attempt is made to
    guess the format from the file suffix. The default format is `json`.

    The UrlLoader recursively follows links to federated repositories in the
    optional `repositories` list for a read index file.
    """
    def __init__(self, url: Optional[str] = None, ftype: Optional[str] = None):
        """Initialize the Url for the repository index file and the file format.

        Uses the Url that is specified in the environment variable *REFDATA_URL*
        as default.

        Raises a ValueError if an invalid file format is given. Valid format
        identifier are `json` or `yaml`.

        Parameters
        ----------
        url: string, default=None
            Url pointing to the repository index document.
        ftype: string, default=None
            Identifier for the file format.
        """
        self.url = url if url is not None else config.URL()
        self.ftype = get_file_format(ftype=ftype, filename=self.url)

    def load(self) -> Dict:
        """Download the repository index file from the given Url.

        Recursively follwos references to other repositories in the optional
        `repositories` list of the downloaded index file.

        Returns
        -------
        dict
        """
        # Load the index file. Raises an error if the HTTP request is not
        # successful.
        r = requests.get(self.url)
        r.raise_for_status()
        # Load response body depending on the specified file format type.
        if self.ftype == FORMAT_YAML:
            body = yaml.load(r.content, Loader=yaml.FullLoader)
        else:
            body = r.json()
        # Create the result containing only the dataset descriptors.
        datasets = body.get('datasets', list())
        # Recursively read additional federated repositories that are specified
        # in the 'repositories' list and add their datasets to the returned
        # result.
        for url in body.get('repositories', list()):
            for obj in UrlLoader(url=url).load().get('datasets'):
                datasets.append(obj)
        return {'datasets': datasets}


# -- Helper Functions ---------------------------------------------------------

def get_file_format(ftype: str, filename: str) -> str:
    """Get the file format identifier.

    If the `ftype` is given it is verified that a valid file format identifier
    is specified. Valid format identifier are `json` and `yaml`. If the identifier
    is valid it is returned. Otherwise, a ValueError is raised.

    If the format identifier is not given, an attempt is made to *guess* the
    format from the suffix of the given file name or Url. Files ending with
    `.json` are assumed to be in Json format and files ending in `.yml` or
    `.yaml` are assumed to be in YAML format. Files that do not match either
    of these suffixes are assumed to be in Json format.

    Parameters
    ----------
    ftype: string
        Identifier for the file format. The giben value may be None.
    filename: string
        Path to file on the file system or Url.

    Returns
    -------
    string
    """
    if ftype is not None:
        if ftype not in FILE_FORMATS:
            raise ValueError("unknown file format '{}'".format(ftype))
        return ftype
    if '.' in filename:
        # Get the file suffix.
        suffix = filename.lower().split('.')[-1]
        if suffix in ['yml', 'yaml']:
            return FORMAT_YAML
    return FORMAT_JSON
