# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Custom error classes raised by different components of the package."""


class RefDataError(Exception):
    """Base class for all custom package errors."""
    pass


class InvalidFormatError(RefDataError):
    """Error that indicates the the format specification for a dataset is
    invalid. The error message contains more details about the cause for
    this error.
    """
    def __init__(self, message: str):
        """Initialize the error message.

        Parameters
        ----------
        message: string
            Detailed error message.
        """
        super(InvalidFormatError, self).__init__(message)


class NotDownloadedError(RefDataError):
    """Error that is raised if an attempt is made to access a dataset has not
    yet been downloaded to the local store.
    """
    def __init__(self, key: str):
        """Initialize the error message.

        Parameters
        ----------
        key: string
            Unique external key for the dataset.
        """
        msg = "dataset '{}' has not been downloaded".format(key)
        super(NotDownloadedError, self).__init__(msg)


class UnknownDatasetError(RefDataError):
    """Error that is raised if an attempt is made to access a dataset that is
    not included in the repository index.
    """
    def __init__(self, key: str):
        """Initialize the error message.

        Parameters
        ----------
        key: string
            Unique external key for the dataset.
        """
        msg = "unknown dataset '{}'".format(key)
        super(UnknownDatasetError, self).__init__(msg)
