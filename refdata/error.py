# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Custom error classes raised by different components of the package."""


class InvalidChecksumError(Exception):
    """Error that is raised when the checksum for a downloaded file does not
    match the checksum that is defined in the repository index.
    """
    def __init__(self, key: str):
        """Initialize the error message.

        Parameters
        ----------
        key: string
            Unique external key for the dataset that was downloaded.
        """
        msg = "invaid checksum for downloaded data file of dataset '{}'".format(key)
        super(InvalidChecksumError, self).__init__(msg)
